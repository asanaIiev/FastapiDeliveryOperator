from sqlalchemy import select
from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.models import Store, UserProfile
from database.schemes import StoreCreateScheme, StoreResponseScheme, StoreUpdateScheme
from .profile import get_current_user
from typing import List

router = APIRouter(prefix='/store', tags=['Store'])

@router.get('/', response_model=List[StoreResponseScheme], tags=['Store'])
async def get_list(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Store))
    return stmt.scalars().all()

@router.get('/{id_}/', response_model=StoreResponseScheme, tags=['Store'])
async def get(id_: int, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(Store).where(Store.id==id_))
    scalar = stmt.scalar_one_or_none()
    return scalar

@router.get('/', response_model=StoreResponseScheme, tags=['Store'])
async def get_your_list(
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = await db.execute(select(Store).where(Store.owner==current_user))
    scalars = stmt.scalars().all()
    return scalars



@router.post('/', response_model=StoreResponseScheme, tags=['Store'])
async def post(
    scheme: StoreCreateScheme,
    db: AsyncSession = Depends(get_db)
):
    store = Store(**scheme.model_dump())

    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store

@router.put('/{id_}/', response_model=StoreResponseScheme, tags=['Store'])
async def put(
    id_: int,
    scheme: StoreUpdateScheme,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = await db.execute(select(Store).where(Store.id==id_,
                                                Store.owner==current_user))
    scalar = stmt.scalar_one_or_none()
    if not scalar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Specified store does not exist')

    update_data = scheme.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(scalar, key, value)

    await db.commit()
    await db.refresh(scalar)
    return scalar

@router.delete('/{id_}/', status_code=status.HTTP_204_NO_CONTENT, tags=['Store'])
async def delete(
    id_: int,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = await db.execute(select(Store).where(Store.id==id_,
                                                Store.owner==current_user))
    scalar = stmt.scalar_one_or_none()
    if not scalar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Specified store does not exist')

    await db.delete(scalar)
    await db.commit()
    return None