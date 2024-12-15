from pydantic import BaseModel
from .models import TrainType, CarriageType
from datetime import time, date, datetime
from typing import List

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
class OrderBase(BaseModel):
    status: str
    created_at: datetime

class OrderCreate(BaseModel):
    user_id: int
    is_through: bool = False
    total_routes: int
    train_run_id: int
    train_run_num_id: int
    start_route_id: int
    start_seq: int
    end_route_id: int
    end_seq: int
    price: float

class OrderOut(OrderBase):
    id: int
    user_id: int | None
    ticket_id: int
    completed_at: datetime | None
    cancelled_at: datetime | None

class OrderOutWithTicket(OrderOut):
    ticket: "TicketOut"

# Train schemas
class TrainBase(BaseModel):
    type: TrainType

class TrainCreate(TrainBase):
    carriages: List["CarriageCreate"] | None = None

class TrainOut(TrainBase):
    id: int
    valid: bool
    deprecated: bool

class TrainOutWithCarriages(TrainOut):
    carriages: List["CarriageOut"] | None

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
    kilometers: int

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
    kilometers: int | None


# TrainRunNum schemas
class TrainRunNumBase(BaseModel):
    name: str

class TrainRunNumCreate(TrainRunNumBase):
    routes: List["RouteCreate"]

class TrainRunNumOut(TrainRunNumBase):
    id: int
    deprecated: bool

class TrainRunNumOutWithRoutes(TrainRunNumOut):
    routes: List["RouteOut"]

class TrainRunNumUpdate(BaseModel):
    name: str | None

class TrainRunNumDeprecate(BaseModel):
    deprecated: bool = True

# TrainRun schemas
class TrainRunBase(BaseModel):
    running_date: date

class TrainRunDemand(TrainRunBase):
    start_station: str
    end_station: str

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

class TrainRunOutWithTrainRunNum(TrainRunBase):
    id: int
    train_run_num: TrainRunNumOutWithRoutes

class TrainRunUpdate(BaseModel):
    date: date | None
    locked: bool | None

class TrainRunFinish(BaseModel):
    finished: bool = True


# Ticket schemas
class TicketOut(BaseModel):
    price: float
    used: bool
    start_sequence: int
    end_sequence: int
    ticket_slot: "TicketSlotOut"

class TicketSlotOut(BaseModel):
    train_run: "TrainRunOutWithTrain"
    seat: "SeatOut"

class SeatOut(BaseModel):
    seat_num: str
    carriage: "CarriageOut"