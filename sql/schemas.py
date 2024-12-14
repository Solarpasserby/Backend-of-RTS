from pydantic import BaseModel
from .models import TrainType, CarriageType
from datetime import time, date

# User schemas
class UserBase(BaseModel):
    name: str
    telephone: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

class UserUpdate(BaseModel):
    name: str | None
    telephone: str | None
    password: str | None

class UserBan(BaseModel):
    banned: bool = True


# Order schemas

# Train schemas
class TrainBase(BaseModel):
    type: TrainType

class TrainCreate(TrainBase):
    carriages: list["CarriageCreate"] | None = None

class TrainOut(TrainBase):
    id: int
    valid: bool
    deprecated: bool

class TrainOutWithCarriages(TrainOut):
    carriages: list["CarriageOut"] | None

class TrainUpdate(BaseModel):
    valid: bool | None

class TrainDeprecate(BaseModel):
    deprecated: bool = True


# Carriage schemas
class CarriageBase(BaseModel):
    num: int
    type: CarriageType

class CarriageCreate(CarriageBase):
    train_id: int | None = None
    seat_rows: int

class CarriageOut(CarriageBase):
    id: int
    deprecated: bool

class CarriageOutWithTrain(CarriageOut):
    train: TrainOut | None

class CarriageUpdate(BaseModel):
    num: int | None
    train_id: int | None

class CarriageDeprecate(BaseModel):
    deprecated: bool = True


# Station schemas
class StationBase(BaseModel):
    name: str
    city: str

class StationCreate(StationBase):
    pass

class StationOut(StationBase):
    id: int
    deprecated: bool

class StationUpdate(BaseModel):
    name: str | None
    city: str | None

class StationDeprecate(BaseModel):
    deprecated: bool = True

# Route schemas
class RouteBase(BaseModel):
    arrival_time: time
    departure_time: time
    sequence: int

class RouteCreate(RouteBase):
    station_name: str

class RouteOut(RouteBase):
    id: int

class RouteOutWithTrainRunNum(RouteOut):
    train_run_num: "TrainRunNumOut"
    station: "StationOut"

class RouteUpdate(BaseModel):
    arrival_time: str | None
    departure_time: str | None
    sequence: int | None

# TrainRunNum schemas
class TrainRunNumBase(BaseModel):
    name: str

class TrainRunNumCreate(TrainRunNumBase):
    routes: list["RouteCreate"]

class TrainRunNumOut(TrainRunNumBase):
    id: int
    deprecated: bool

class TrainRunNumOutWithRoutes(TrainRunNumOut):
    routes: list["RouteOut"]

class TrainRunNumUpdate(BaseModel):
    name: str | None

class TrainRunNumDeprecate(BaseModel):
    deprecated: bool = True

# TrainRun schemas
class TrainRunBase(BaseModel):
    date: date

class TrainRunCreate(TrainRunBase):
    train_id: int
    train_run_num_id: int

class TrainRunOut(TrainRunBase):
    id: int
    train_id: int
    train_run_num_id: int

class TrainRunOutWithTrain(TrainRunBase):
    id: int
    train: TrainOut
    train_run_num: TrainRunNumOut

class TrainRunUpdate(BaseModel):
    date: date | None
    train_id: int | None
    train_run_num_id: int | None

class TrainRunFinish(BaseModel):
    finished: bool = True