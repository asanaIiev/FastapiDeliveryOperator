from jose import jwt 
from database.connection import get_db
from database.models import UserProfile, UserRefresh
from database.schemes import UserCreateScheme, UserLoginScheme, UserRefreshScheme, UserResponseScheme
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from config import settings
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, APIRouter, Depends
from sqlalchemy import select, delete

router = APIRouter(prefix='/auth', tags=['Authorization'])

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expiration_time = datetime.now(timezone.utc) + expires_delta
    to_encode.update({'exp': expiration_time})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(user: UserProfile) -> str:
    return create_token({
        'sub': str(user.id),
        'token_type': 'access'
    }, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME))

def create_refresh_token(user: UserProfile) -> str:
    return create_token({
        'sub': str(user.id),
        'token_type': 'refresh'
    }, expires_delta=timedelta(days=settings.REFERSH_TOKEN_LIFETIME))

@router.post('/register', response_model=dict, tags=['Authorization'])
async def register(
    scheme: UserCreateScheme,
    db: AsyncSession = Depends(get_db)
):
    username_res = await db.execute(select(UserProfile).where(UserProfile.username==scheme.username))
    username_scal = username_res.scalar_one_or_none()

    if username_scal:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This username is already taken')

    if scheme.email:
        email_res = await db.execute(select(UserProfile).where(UserProfile.email==scheme.email))
        email_scal = email_res.scalar_one_or_none()

        if email_scal:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This email is already taken')

    if scheme.phone:
        phone_res = await db.execute(select(UserProfile).where(UserProfile.phone==scheme.phone))
        phone_scal = phone_res.scalar_one_or_none()

        if phone_scal:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This phone number is already in use')

    update_data = scheme.model_dump()
    update_data['password'] = hash_password(scheme.password)
    user = UserProfile(**update_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {'detail': 'Successfully registered in'}


@router.post('/login', response_model=dict, tags=['Authorization'])
async def login(
    scheme: UserLoginScheme,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserProfile).where(UserProfile.username==scheme.username))
    scalar = result.scalar_one_or_none()

    if not scalar or not verify_password(scheme.password, scalar.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    access_token = create_access_token(scalar)
    refresh_token = create_refresh_token(scalar)
    refresh = UserRefresh(user_id=scalar.id, token=refresh_token)

    db.add(refresh)
    await db.commit()
    await db.refresh(refresh)
    return {
        'detail': 'Successfully logged in',
        'access': access_token,
        'refresh': refresh_token,
        'token_type': 'Bearer'
    }


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT, tags=['Authorization'])
async def logout(
    scheme: UserRefreshScheme,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserRefresh).where(UserRefresh.token==scheme.refresh_token))
    scalar = result.scalar_one_or_none()

    if not scalar:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')

    await db.execute(delete(UserRefresh).where(UserRefresh.user_id==scalar.user_id))
    await db.commit()
    return None


@router.post('/access', response_model=dict, tags=['Authorization'])
async def access(
    scheme: UserRefreshScheme,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserRefresh).where(UserRefresh.token==scheme.refresh_token))
    scalar = result.scalar_one_or_none()

    if not scalar:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')

    user_res = await db.execute(select(UserProfile).where(UserProfile.id==scalar.user_id))
    user_scal = user_res.scalar_one_or_none()

    access_token = create_access_token(user_scal)
    return {
        'access': access_token,
        'token_type': 'Bearer'
    }