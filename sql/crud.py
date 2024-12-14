from fastapi import HTTPException
from sqlmodel import Session, select
from sql.models import User, Train, Carriage, Seat, Station, TrainRunNum, Route, TrainRun
from sql.schemas import UserCreate, UserUpdate
from sql.schemas import CarriageCreate, CarriageUpdate
from sql.schemas import StationCreate, StationUpdate
from sql.schemas import TrainCreate, TrainUpdate
from sql.schemas import TrainRunNumCreate, TrainRunNumUpdate
from sql.schemas import RouteUpdate
from sql.schemas import TrainRunCreate, TrainRunUpdate

train_dict = {
    "fast": ["second_class", "first_class", "business"],
    "slow": ["second_class", "first_class"]
}
carriage_dict = {
    "second_class": [12, 16],
    "first_class": [10, 12],
    "business": [8]
}
seat_dict = {
    "second_class": 5,
    "first_class": 4,
    "business": 3
}
seat_num_dict = {
    "second_class": ["A", "B", "C", "D", "F"],
    "first_class": ["A", "C", "D", "F"],
    "business": ["A", "C", "F"]
}


# User CRUD
def get_user(user_id: int, session: Session):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def add_user(user: UserCreate, session: Session):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def remove_user(user_id: int, session: Session):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}

def modify_user(user_id: int, user: UserUpdate, session: Session):
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def set_user_ban(user_id: int, banned: bool, session: Session):
    db_user = session.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.banned = banned
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# Order CRUD

# Carriage CRUD
def get_carriage(carriage_id: int, session: Session):
    carriage = session.get(Carriage, carriage_id)
    if carriage is None:
        raise HTTPException(status_code=404, detail="Carriage not found")
    return carriage

def add_carriage(carriage: CarriageCreate, session: Session, train_id: int | None = None, auto_commit: bool = True):
    if train_id is not None:
        train = session.get(Train, train_id)
        if train is None:
            raise HTTPException(status_code=404, detail="Train not found")
        if carriage.type not in train_dict[train.type]:
            raise HTTPException(status_code=400, detail="Invalid carriage type")

    if carriage.seat_rows not in carriage_dict[carriage.type]:
        raise HTTPException(status_code=400, detail="Invalid seat rows")

    carriage_data = carriage.model_dump()
    seat_rows = carriage_data.pop("seat_rows")
    db_carriage = Carriage.model_validate(carriage_data)
    db_carriage.train = train
    session.add(db_carriage)
    session.flush()

    row_seats = seat_dict[carriage.type]
    for i in range(seat_rows):
        for j in range(row_seats):
            num = f"{i+1}{seat_num_dict[carriage.type][j]}"
            seat = Seat(carriage_id=db_carriage.id, seat_num=num)
            session.add(seat)

    if auto_commit:
        session.commit()
        session.refresh(db_carriage)
        return db_carriage

def remove_carriage(carriage_id: int, session: Session):
    carriage = session.get(Carriage, carriage_id)
    if carriage is None:
        raise HTTPException(status_code=404, detail="Carriage not found")
    if carriage.train:
        raise HTTPException(status_code=400, detail="Carriage has been used in train")
    if carriage.deprecated:
        raise HTTPException(status_code=400, detail="You can't delete deprecated carriage")
    session.delete(carriage)
    session.commit()
    return {"message": "Carriage deleted successfully"}

def modify_carriage(carriage_id: int, carriage: CarriageUpdate, session: Session):
    if carriage.train_id is not None:
        train = session.get(Train, carriage.train_id)
        if carriage.type not in train_dict[train.type]:
            raise HTTPException(status_code=400, detail="Invalid carriage type")

    db_carriage = session.get(Carriage, carriage_id)
    if db_carriage is None:
        raise HTTPException(status_code=404, detail="Carriage not found")
    carriage_data = carriage.model_dump(exclude_unset=True)
    db_carriage.sqlmodel_update(carriage_data)
    session.add(db_carriage)
    session.commit()
    session.refresh(db_carriage)
    return db_carriage

def set_carriage_deprecated(carriage_id: int, deprecated: bool, session: Session):
    db_carriage = session.get(Carriage, carriage_id)
    if db_carriage is None:
        raise HTTPException(status_code=404, detail="Carriage not found")
    db_carriage.deprecated = deprecated
    session.add(db_carriage)
    session.commit()
    session.refresh(db_carriage)
    return db_carriage


# Train CRUD
def get_train(train_id: int, session: Session):
    train = session.get(Train, train_id)
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    return train

def add_train(train: TrainCreate, session: Session):
    train_data = train.model_dump()
    train_data.pop("carriages")
    db_train = Train.model_validate(train_data)
    session.add(db_train)
    session.flush()

    if train.carriages is not None:
        for carriage in train.carriages:
            add_carriage(carriage, session, db_train.id, auto_commit=False)

    session.commit()
    return db_train

def remove_train(train_id: int, session: Session):
    train = session.get(Train, train_id)
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    if train.train_runs:
        raise HTTPException(status_code=400, detail="Train has been used in train runs")
    if train.valid:
        raise HTTPException(status_code=400, detail="You can't delete valid train")
    if train.deprecated:
        raise HTTPException(status_code=400, detail="You can't delete deprecated train")
    session.delete(train)
    session.commit()
    return {"message": "Train deleted successfully"}

def modify_train(train_id: int, train: TrainUpdate, session: Session):
    db_train = session.get(Train, train_id)
    if db_train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    train_data = train.model_dump(exclude_unset=True)
    db_train.sqlmodel_update(train_data)
    session.add(db_train)
    session.commit()
    session.refresh(db_train)
    return db_train

def set_train_deprecated(train_id: int, deprecated: bool, session: Session):
    db_train = session.get(Train, train_id)
    if db_train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    db_train.deprecated = deprecated
    session.add(db_train)
    session.commit()
    session.refresh(db_train)
    return db_train

# Station CRUD
def get_station(station_id: int, session: Session):
    station = session.get(Station, station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return station

def add_station(station: StationCreate, session: Session):
    db_station = Station.model_validate(station)
    session.add(db_station)
    session.commit()
    session.refresh(db_station)
    return db_station

def remove_station(station_id: int, session: Session):
    station = session.get(Station, station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    if station.routes:
        raise HTTPException(status_code=400, detail="Station has been used in routes")
    if station.deprecated:
        raise HTTPException(status_code=400, detail="You can't delete deprecated station")
    session.delete(station)
    session.commit()
    return {"message": "Station deleted successfully"}

def modify_station(station_id: int, station: StationUpdate, session: Session):
    db_station = session.get(Station, station_id)
    if db_station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    station_data = station.model_dump(exclude_unset=True)
    db_station.sqlmodel_update(station_data)
    session.add(db_station)
    session.commit()
    session.refresh(db_station)
    return db_station

def set_station_deprecated(station_id: int, deprecated: bool, session: Session):
    db_station = session.get(Station, station_id)
    if db_station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    db_station.deprecated = deprecated
    session.add(db_station)
    session.commit()
    session.refresh(db_station)
    return db_station


# TrainRunNum CRUD
def get_train_run_num(train_run_num_id: int, session: Session):
    train_run_num = session.get(TrainRunNum, train_run_num_id)
    if train_run_num is None:
        raise HTTPException(status_code=404, detail="TrainRunNum not found")
    return train_run_num

def add_train_run_num(train_run_num: TrainRunNumCreate, session: Session):
    train_run_num_data = train_run_num.model_dump()
    routes = train_run_num_data.pop("routes")
    db_train_run_num = TrainRunNum.model_validate(train_run_num_data)
    session.add(db_train_run_num)

    for route in train_run_num.routes:
        route_data = route.model_dump()
        station_name = route_data.pop("station_name")
        station = session.exec(select(Station).where(Station.name == station_name)).first()
        print(station)
        if station is None:
            raise HTTPException(status_code=404, detail="Station not found")
        db_route = Route(**route_data)
        db_route.station = station
        db_train_run_num.routes.append(db_route)

    session.commit()
    session.refresh(db_train_run_num)
    return db_train_run_num

def remove_train_run_num(train_run_num_id: int, session: Session):
    train_run_num = session.get(TrainRunNum, train_run_num_id)
    if train_run_num is None:
        raise HTTPException(status_code=404, detail="TrainRunNum not found")
    if train_run_num.train_runs:
        raise HTTPException(status_code=400, detail="TrainRunNum has been used in train runs")
    if train_run_num.deprecated:
        raise HTTPException(status_code=400, detail="You can't delete deprecated train run num")
    session.delete(train_run_num)
    session.commit()
    return {"message": "TrainRunNum deleted successfully"}

def modify_train_run_num(train_run_num_id: int, train_run_num: TrainRunNumUpdate, session: Session):
    db_train_run_num = session.get(TrainRunNum, train_run_num_id)
    if db_train_run_num is None:
        raise HTTPException(status_code=404, detail="TrainRunNum not found")
    train_run_num_data = train_run_num.model_dump(exclude_unset=True)
    db_train_run_num.sqlmodel_update(train_run_num_data)
    session.add(db_train_run_num)
    session.commit()
    session.refresh(db_train_run_num)
    return db_train_run_num

def set_train_run_num_deprecated(train_run_num_id: int, deprecated: bool, session: Session):
    db_train_run_num = session.get(TrainRunNum, train_run_num_id)
    if db_train_run_num is None:
        raise HTTPException(status_code=404, detail="TrainRunNum not found")
    db_train_run_num.deprecated = deprecated
    session.add(db_train_run_num)
    session.commit()
    session.refresh(db_train_run_num)
    return db_train_run_num

# Route CRUD
def get_route(route_id: int, session: Session):
    route = session.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

def modify_route(route_id: int, route: RouteUpdate, session: Session):
    db_route = session.get(Route, route_id)
    if db_route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    route_data = route.model_dump(exclude_unset=True)
    db_route.sqlmodel_update(route_data)
    session.add(db_route)
    session.commit()
    session.refresh(db_route)
    return db_route

# TrainRun CRUD
def get_train_run(train_run_id: int, session: Session):
    train_run = session.get(TrainRun, train_run_id)
    if train_run is None:
        raise HTTPException(status_code=404, detail="TrainRun not found")
    return train_run

def add_train_run(train_run: TrainRunCreate, session: Session):
    train = session.get(Train, train_run.train_id)
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    train_run_num = session.get(TrainRunNum, train_run.train_run_num_id)
    if train_run_num is None:
        raise HTTPException(status_code=404, detail="TrainRunNum not found")

    db_train_run = TrainRun.model_validate(train_run)
    db_train_run.train = train
    db_train_run.train_run_num = train_run_num
    session.add(db_train_run)
    session.commit()
    session.refresh(db_train_run)
    return db_train_run

def remove_train_run(train_run_id: int, session: Session):
    train_run = session.get(TrainRun, train_run_id)
    if train_run is None:
        raise HTTPException(status_code=404, detail="TrainRun not found")
    if train_run.finished:
        raise HTTPException(status_code=400, detail="You can't delete finished train run")
    if train_run.tickets:
        raise HTTPException(status_code=400, detail="TrainRun has been used in tickets")
    session.delete(train_run)
    session.commit()
    return {"message": "TrainRun deleted successfully"}

def modify_train_run(train_run_id: int, train_run: TrainRunUpdate, session: Session):
    db_train_run = session.get(TrainRun, train_run_id)
    if db_train_run is None:
        raise HTTPException(status_code=404, detail="TrainRun not found")
    if db_train_run.tickets:
        raise HTTPException(status_code=400, detail="The tickets have been sold")
    train = session.get(Train, train_run.train_id)
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    train_run_num = session.get(TrainRunNum, train_run.train_run_num_id)
    if train_run_num is None:
        raise HTTPException(status_code=404, detail="TrainRunNum not found")

    train_run_data = train_run.model_dump(exclude_unset=True)
    db_train_run.sqlmodel_update(train_run_data)
    db_train_run.train = train
    db_train_run.train_run_num = train_run_num
    session.add(db_train_run)
    session.commit()
    session.refresh(db_train_run)
    return db_train_run

def set_train_run_finished(train_run_id: int, finished: bool, session: Session):
    db_train_run = session.get(TrainRun, train_run_id)
    if db_train_run is None:
        raise HTTPException(status_code=404, detail="TrainRun not found")
    db_train_run.finished = finished
    session.add(db_train_run)
    session.commit()
    session.refresh(db_train_run)
    return db_train_run