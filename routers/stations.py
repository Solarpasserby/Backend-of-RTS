from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated
from sql.database import engine
from sql.schemas import StationCreate, StationOut, StationUpdate, StationDeprecate
from sql.crud import get_station, add_station, remove_station, modify_station, set_station_deprecated

def get_session():
    with Session(engine) as session:
        yield session

sessionDepends = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{station_id}", response_model=StationOut)
async def read_station(station_id: int, session: sessionDepends):
    return get_station(station_id, session)

@router.post("/create", response_model=StationOut)
async def create_station(station: StationCreate, session: sessionDepends):
    return add_station(station, session)

@router.delete("/{station_id}")
def delete_station(station_id: int, session: sessionDepends):
    return remove_station(station_id, session)

@router.patch("/{station_id}", response_model=StationOut)
async def update_station(station_id: int, station: StationUpdate, session: sessionDepends):
    return modify_station(station_id, station, session)

@router.patch("/{station_id}/deprecated", response_model=StationOut)
def set_station_deprecated(station_id: int, station: StationDeprecate, session: sessionDepends):
    return set_station_deprecated(station_id, station.deprecated, session)