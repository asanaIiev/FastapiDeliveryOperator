from jose import jwt, JWTError
from database.connection import get_db
from database.models import UserProfile, UserRefresh
from database.schemes import UserCreateScheme, UserLoginScheme, UserRefreshScheme
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, delete
from .security import hash_password, verify_password

router = APIRouter(prefix='/auth', tags=['Authorization'])

def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expiration_time = datetime.now(timezone.utc) + expires_delta
    to_encode.update({'exp': expiration_time})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(user: UserProfile) -> str:
    return create_token({
        'sub': str(user.id),
        'token_type': 'access',
        'jti': uuid4().hex,
    }, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME))

def create_refresh_token(user: UserProfile) -> str:
    return create_token({
        'sub': str(user.id),
        'token_type': 'refresh',
        'jti': uuid4().hex,
    }, expires_delta=timedelta(days=settings.REFERSH_TOKEN_LIFETIME))


async def issue_tokens(username: str, password: str, db: AsyncSession) -> dict[str, str]:
    result = await db.execute(select(UserProfile).where(UserProfile.username == username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    refresh = UserRefresh(user_id=user.id, token=refresh_token)
    db.add(refresh)
    await db.commit()

    return {
        'access': access_token,
        'refresh': refresh_token,
        'token_type': 'Bearer',
    }


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
    tokens = await issue_tokens(scheme.username, scheme.password, db)
    return {'detail': 'Successfully logged in', **tokens}


@router.post('/token', tags=['Authorization'])
async def login_with_oauth_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    tokens = await issue_tokens(form_data.username, form_data.password, db)
    return {
        'access_token': tokens['access'],
        'refresh_token': tokens['refresh'],
        'token_type': 'bearer',
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

    try:
        payload = jwt.decode(
            scheme.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if (
            payload.get('token_type') != 'refresh'
            or payload.get('sub') != str(scalar.user_id)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid or expired token',
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
        )

    user_res = await db.execute(select(UserProfile).where(UserProfile.id==scalar.user_id))
    user_scal = user_res.scalar_one_or_none()
    if user_scal is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid or expired token')

    access_token = create_access_token(user_scal)
    return {
        'access': access_token,
        'token_type': 'Bearer'
    }