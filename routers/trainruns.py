from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Annotated, List
from sql.database import engine
from sql.schemas import TrainRunCreate, TrainRunOut, TrainRunOutWithTrain, TrainRunUpdate, TrainRunFinish, TrainRunOutWithTrainRunNum, TrainRunDemand
from sql.crud import get_train_run, add_train_run, remove_train_run, modify_train_run, set_train_run_finished, get_train_runs_by_demand, get_train_runs

def get_session():
    with Session(engine) as session:
        yield session

sessionDepends = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/train_runs",
    tags=["train_runs"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{train_run_id}", response_model=TrainRunOutWithTrain)
async def read_train_run(train_run_id: int, session: sessionDepends):
    return get_train_run(train_run_id, session)

@router.get("/", response_model=List[TrainRunOutWithTrain])
async def read_train_runs(offset: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    return get_train_runs(offset, limit, session)

@router.get("/demand", response_model=List[TrainRunOutWithTrainRunNum])
async def read_train_runs_by_demand(demand: TrainRunDemand, session: sessionDepends):
    return get_train_runs_by_demand(demand, session)

@router.post("/create", response_model=TrainRunOut)
async def create_train_run(train_run: TrainRunCreate, session: sessionDepends):
    return add_train_run(train_run, session)

@router.delete("/{train_run_id}")
def delete_train_run(train_run_id: int, session: sessionDepends):
    return remove_train_run(train_run_id, session)

@router.patch("/{train_run_id}", response_model=TrainRunOut)
async def update_train_run(train_run_id: int, train_run: TrainRunUpdate, session: sessionDepends):
    return modify_train_run(train_run_id, train_run, session)

@router.patch("/{train_run_id}/finish", response_model=TrainRunOut)
def finish_train_run(train_run_id: int, train_run: TrainRunFinish, session: sessionDepends):
    return set_train_run_finished(train_run_id, train_run.finished, session)