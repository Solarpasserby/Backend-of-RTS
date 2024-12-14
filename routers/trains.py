from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
from sql.database import engine
from sql.schemas import TrainCreate, TrainOut, TrainOutWithCarriages, TrainUpdate, TrainDeprecate
from sql.crud import get_train, add_train, remove_train, modify_train, set_train_deprecated

def get_session():
    with Session(engine) as session:
        yield session

sessionDepends = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/trains",
    tags=["trains"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{train_id}", response_model=TrainOutWithCarriages)
async def read_train(train_id: int, session: sessionDepends):
    return get_train(train_id, session)

@router.post("/create", response_model=TrainOut)
async def create_train(train: TrainCreate, session: sessionDepends):
    return add_train(train, session)

@router.delete("/{train_id}")
def delete_train(train_id: int, session: sessionDepends):
    return remove_train(train_id, session)

@router.patch("/{train_id}", response_model=TrainOut)
def update_train(train_id: int, train: TrainUpdate, session: sessionDepends):
    return modify_train(train_id, train, session)

@router.patch("/{train_id}/deprecate", response_model=TrainOut)
def deprecate_train(train_id: int, train: TrainDeprecate, session: sessionDepends):
    return set_train_deprecated(train_id, train.deprecated, session)