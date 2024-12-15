from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
from sql.database import engine
from sql.schemas import CarriageCreate, CarriageOut, CarriageOutWithTrain, CarriageUpdate, CarriageDeprecate
from sql.crud import get_carriage, add_carriage, remove_carriage, modify_carriage, set_carriage_deprecated

def get_session():
    with Session(engine) as session:
        yield session

sessionDepends = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/carriages",
    tags=["carriages"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{carriage_id}", response_model=CarriageOutWithTrain)
async def read_carriage(carriage_id: int, session: sessionDepends):
    return get_carriage(carriage_id, session)

@router.post("/create", response_model=CarriageOut)
async def create_carriage(carriage: CarriageCreate, session: sessionDepends):
    return add_carriage(carriage, session)

@router.delete("/{carriage_id}")
def delete_carriage(carriage_id: int, session: sessionDepends):
    return remove_carriage(carriage_id, session)

@router.patch("/{carriage_id}", response_model=CarriageOut)
def update_carriage(carriage_id: int, carriage: CarriageUpdate, session: sessionDepends):
    return modify_carriage(carriage_id, carriage, session)

@router.patch("/{carriage_id}/deprecate", response_model=CarriageOut)
def deprecate_carriage(carriage_id: int, carriage: CarriageDeprecate, session: sessionDepends):
    return set_carriage_deprecated(carriage_id, carriage.deprecated, session)