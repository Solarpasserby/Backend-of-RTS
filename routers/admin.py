from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
from enum import Enum
from sql.database import engine
from sql.schemas import AdminLogin, AdminOut
from sql.crud import authenticate_admin, get_count

class CountQueryEnum(str, Enum):
    users = "users"
    orders = "orders"
    trains = "trains"
    stations = "stations"
    runs = "runs"
    nums = "nums"


def get_session():
    with Session(engine) as session:
        yield session

sessionDepends = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=AdminOut)
async def check_admin_login(admin: AdminLogin, session: sessionDepends):
    return authenticate_admin(admin, session)

@router.get("/count")
async def get_admin_count(query: CountQueryEnum, session: sessionDepends):
    return get_count(query, session)