from sqlalchemy import delete as sql_delete, select
from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.models import UserProfile, UserRefresh
from database.schemes import UserResponseScheme, UserUpdateScheme
from typing import Annotated
from jose import jwt, JWTError
from config import settings
from fastapi.security import OAuth2PasswordBearer
from .security import hash_password

router = APIRouter(prefix='/profile', tags=['Profile'])

oauth2scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

async def get_current_user(
        token: Annotated[str, Depends(oauth2scheme)],
        db: AsyncSession = Depends(get_db)
) -> UserProfile:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not authorize credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get('token_type') != 'access':
            raise credentials_exception
        subject = payload.get('sub')
        if subject is None:
            raise credentials_exception
        user_id = int(subject)

    except (JWTError, TypeError, ValueError):
        raise credentials_exception

    result = await db.execute(select(UserProfile).where(UserProfile.id==user_id))
    scalar = result.scalar_one_or_none()

    if not scalar:
        raise credentials_exception

    refresh_res = await db.execute(
        select(UserRefresh).where(UserRefresh.user_id==scalar.id)
    )
    refresh_scal = refresh_res.scalars().first()
    if not refresh_scal:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Session has been closed (logged out)',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return scalar

@router.get('/', response_model=UserResponseScheme, tags=['Profile'])
async def get(current_user: UserProfile = Depends(get_current_user)):
    return current_user

@router.put('/', response_model=UserResponseScheme, tags=['Profile'])
async def put(
    scheme: UserUpdateScheme,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    update_data = scheme.model_dump(exclude_unset=True)
    if any(update_data.get(field) is None for field in ('username', 'password') if field in update_data):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Username and password cannot be null',
        )

    if 'username' in update_data:
        result = await db.execute(
            select(UserProfile).where(
                UserProfile.username == update_data['username'],
                UserProfile.id != current_user.id,
            )
        )
        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This username is already taken')

    if 'email' in update_data and update_data['email'] is not None:
        result = await db.execute(
            select(UserProfile).where(
                UserProfile.email == update_data['email'],
                UserProfile.id != current_user.id,
            )
        )
        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This email is already taken')

    if 'phone' in update_data and update_data['phone'] is not None:
        result = await db.execute(
            select(UserProfile).where(
                UserProfile.phone == update_data['phone'],
                UserProfile.id != current_user.id,
            )
        )
        if result.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='This phone number is already in use')

    if 'password' in update_data:
        update_data['password'] = hash_password(update_data['password'])

    for key, value in update_data.items():
        setattr(current_user, key, value)

    if 'password' in update_data:
        await db.execute(
            sql_delete(UserRefresh).where(UserRefresh.user_id == current_user.id)
        )

    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.delete('/', response_model=dict, tags=['Profile'])
async def delete(
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await db.delete(current_user)
    await db.commit()
    return {'detail': 'Your account has been deleted'}