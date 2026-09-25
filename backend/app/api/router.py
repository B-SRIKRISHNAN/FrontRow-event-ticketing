from fastapi import APIRouter

from app.api.v1 import auth, events, holds, checkout, orders

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(events.router, prefix="/events", tags=["Events & Seats"])
api_router.include_router(holds.router, tags=["Seat Holds"])
api_router.include_router(checkout.router, tags=["Checkout"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
