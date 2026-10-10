from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.models import Product, Store, UserProfile
from database.schemes import *
from .profile import get_current_user

router = APIRouter(prefix='/product', tags=['Product'])

@router.get('/', response_model=List[ProductResponseScheme])
async def get_list(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    return result.scalars().all()

@router.get('/my/', response_model=List[ProductResponseScheme])
async def get_my_list(
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product)
        .join(Store, Product.store == Store.id)
        .where(Store.owner == current_user.id)
    )
    return result.scalars().all()

@router.get('/my/{id_}/', response_model=ProductResponseScheme)
async def get_my(
    id_: int,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product)
        .join(Store, Product.store == Store.id)
        .where(Product.id == id_, Store.owner == current_user.id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Specified product does not exist',
        )
    return product

@router.get('/{id_}/', response_model=ProductResponseScheme)
async def get(id_: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == id_))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Specified product does not exist',
        )
    return product

@router.post('/', response_model=ProductResponseScheme)
async def post(
    scheme: ProductCreateScheme,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Store).where(
            Store.id == scheme.store,
            Store.owner == current_user.id,
        )
    )
    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Specified store does not exist',
        )

    product = Product(**scheme.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@router.put('/{id_}/', response_model=ProductResponseScheme)
async def put(
    id_: int,
    scheme: ProductUpdateScheme,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product)
        .join(Store, Product.store == Store.id)
        .where(Product.id == id_, Store.owner == current_user.id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Specified product does not exist',
        )

    update_data = scheme.model_dump(exclude_unset=True)
    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Product fields cannot be null',
        )

    if 'store' in update_data:
        store_result = await db.execute(
            select(Store).where(
                Store.id == update_data['store'],
                Store.owner == current_user.id,
            )
        )
        if store_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Specified store does not exist',
            )

    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return product

@router.delete('/{id_}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id_: int,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product)
        .join(Store, Product.store == Store.id)
        .where(Product.id == id_, Store.owner == current_user.id)
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Specified product does not exist',
        )

    await db.delete(product)
    await db.commit()
