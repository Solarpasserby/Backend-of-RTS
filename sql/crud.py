from fastapi import HTTPException
from sqlmodel import Session, select
from sql.models import User, Train, Carriage, Seat, Station
from sql.schemas import UserCreate, UserUpdate
from sql.schemas import CarriageCreate, CarriageUpdate
from sql.schemas import StationCreate, StationUpdate
from sql.schemas import TrainCreate, TrainUpdate

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