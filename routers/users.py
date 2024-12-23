from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated, List
from sql.database import engine
from sql.schemas import UserCreate, UserOut, UserUpdate, UserBan, UserLogin
from sql.crud import get_user, add_user, remove_user, modify_user, set_user_ban, authenticate_user, get_users

def get_session():
    with Session(engine) as session:
        yield session

sessionDepends = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: int, session: sessionDepends):
    return get_user(user_id, session)

@router.get("/", response_model=List[UserOut])
async def read_users(offset: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    return get_users(offset, limit, session)

@router.post("/login", response_model=UserOut)
async def check_user_login(user: UserLogin, session: sessionDepends):
    return authenticate_user(user, session)

@router.post("/create", response_model=UserOut)
async def create_user(user: UserCreate, session: sessionDepends):
    return add_user(user, session)

@router.delete("/{user_id}")
def delete_user(user_id: int, session: sessionDepends):
    return remove_user(user_id, session)

@router.patch("/{user_id}", response_model=UserOut)
async def update_user(user_id: int, user: UserUpdate, session: sessionDepends):
    return modify_user(user_id, user, session)

@router.patch("/{user_id}/banned", response_model=UserOut)
def ban_user(user_id: int, user: UserBan, session: sessionDepends):
    return set_user_ban(user_id, user.banned, session)