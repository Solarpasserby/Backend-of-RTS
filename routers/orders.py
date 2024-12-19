from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated, List
from sql.database import engine
from sql.schemas import OrderCreate, OrderOut, OrderOutWithTicket
from sql.crud import get_order, get_orders_by_user, add_order, complete_order, cancel_order, remove_order, get_orders

def get_session():
    with Session(engine) as session:
        yield session

sessionDepends = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{order_id}", response_model=OrderOutWithTicket)
async def read_order(order_id: int, session: sessionDepends):
    return get_order(order_id, session)

@router.get("/", response_model=List[OrderOutWithTicket])
async def read_orders(offset: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    return get_orders(offset, limit, session)

@router.get("/user/{user_id}", response_model=List[OrderOutWithTicket])
async def read_orders_by_user(user_id: int, session: sessionDepends):
    return get_orders_by_user(user_id, session)

@router.post("/create", response_model=OrderOut)
async def create_order(order: OrderCreate, session: sessionDepends):
    return add_order(order, session)

@router.patch("/{order_id}/complete", response_model=OrderOut)
def set_order_completed(order_id: int, session: sessionDepends):
    return complete_order(order_id, session)

@router.patch("/{order_id}/cancel", response_model=OrderOut)
def set_order_cancelled(order_id: int, session: sessionDepends):
    return cancel_order(order_id, session)

@router.delete("/{order_id}")
def delete_order(order_id: int, session: sessionDepends):
    return remove_order(order_id, session)