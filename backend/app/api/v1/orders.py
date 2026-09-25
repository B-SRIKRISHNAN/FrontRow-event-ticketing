from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.domain import Order, User
from app.schemas.dto import OrderResponse

router = APIRouter()


@router.get("", response_model=List[OrderResponse])
async def list_user_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Principle II: Filter orders strictly by JWT user ID claim
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.tickets))
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    return orders
