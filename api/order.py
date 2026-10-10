from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from database.models import Order, UserProfile, Product
from database.schemes import OrderCreateScheme, OrderResponseScheme
from .profile import get_current_user
from typing import List

router = APIRouter(prefix='/order', tags=['Order'])

@router.get('/', response_model=List[OrderResponseScheme], tags=['Order'])
async def get_list(
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = await db.execute(select(Order).where(Order.user==current_user.id))
    return stmt.scalars().all()

@router.post('/', response_model=OrderResponseScheme, tags=['Order'])
async def post(
    scheme: OrderCreateScheme,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = await db.execute(select(Product).where(Product.id==scheme.product))
    scalar = stmt.scalar_one_or_none()

    if not scalar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Specified product does not exist')

    order = Order(user=current_user.id, **scheme.model_dump())

    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order

@router.delete('/{id_}/', status_code=status.HTTP_204_NO_CONTENT, tags=['Order'])
async def delete(
    id_: int,
    current_user: UserProfile = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = await db.execute(select(Order).where(Order.id==id_,
                                                Order.user==current_user.id))
    scalar = stmt.scalar_one_or_none()
    if not scalar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Specified order does not exist')

    await db.delete(scalar)
    await db.commit()
    return None