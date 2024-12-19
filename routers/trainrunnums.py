from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated, List
from sql.database import engine
from sql.schemas import TrainRunNumCreate, TrainRunNumOut, TrainRunNumOutWithRoutes, TrainRunNumUpdate, TrainRunNumDeprecate
from sql.schemas import RouteOut, RouteOutWithTrainRunNum, RouteUpdate
from sql.crud import get_train_run_num, add_train_run_num, remove_train_run_num, modify_train_run_num, set_train_run_num_deprecated, get_train_run_nums
from sql.crud import get_route, modify_route

def get_session():
    with Session(engine) as session:
        yield session

sessionDepends = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/train_run_nums",
    tags=["train_run_nums"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{train_run_num_id}", response_model=TrainRunNumOutWithRoutes)
async def read_train_run_num(train_run_num_id: int, session: sessionDepends):
    return get_train_run_num(train_run_num_id, session)

@router.get("/", response_model=List[TrainRunNumOut])
async def read_train_run_nums(offset: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    return get_train_run_nums(offset, limit, session)

@router.post("/create", response_model=TrainRunNumOut)
async def create_train_run_num(train_run_num: TrainRunNumCreate, session: sessionDepends):
    return add_train_run_num(train_run_num, session)

@router.delete("/{train_run_num_id}")
def delete_train_run_num(train_run_num_id: int, session: sessionDepends):
    return remove_train_run_num(train_run_num_id, session)

@router.patch("/{train_run_num_id}", response_model=TrainRunNumOut)
async def update_train_run_num(train_run_num_id: int, train_run_num: TrainRunNumUpdate, session: sessionDepends):
    return modify_train_run_num(train_run_num_id, train_run_num, session)

@router.patch("/{train_run_num_id}/deprecated", response_model=TrainRunNumOut)
def deprecate_train_run_num(train_run_num_id: int, train_run_num: TrainRunNumDeprecate, session: sessionDepends):
    return set_train_run_num_deprecated(train_run_num_id, train_run_num.deprecated, session)

@router.get("/route/{route_id}", response_model=RouteOutWithTrainRunNum)
async def read_route(route_id: int, session: sessionDepends):
    return get_route(route_id, session)

@router.patch("/route/{route_id}", response_model=RouteOut)
async def update_route(route_id: int, route: RouteUpdate, session: sessionDepends):
    return modify_route(route_id, route, session)