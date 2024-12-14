from email.policy import default

from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime, date, time

class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class TicketStatus(str, Enum):
    available = "available"
    sold = "sold"
    used = "used"

class TrainType(str, Enum):
    fast = "fast"
    slow = "slow"

class CarriageType(str, Enum):
    second_class = "second_class"
    first_class = "first_class"
    business = "business"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    telephone: str
    password: str
    banned: bool = False

    orders: list["Order"] = Relationship(back_populates="user")


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(foreign_key="user.id")
    ticket_id: int = Field(foreign_key="ticket.id")
    status: OrderStatus
    created_at: datetime
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None

    user: User | None = Relationship(back_populates="orders")
    ticket: "Ticket" = Relationship(back_populates="order")


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    train_run_id: int = Field(foreign_key="train_run.id")
    seat_id: int = Field(foreign_key="seat.id")
    price: float
    status: TicketStatus
    start_station: str | None = None
    end_station: str | None = None

    train_run: "TrainRun" = Relationship(back_populates="tickets")
    seat: "Seat" = Relationship(back_populates="tickets")
    order: Order = Relationship(back_populates="ticket")


class TrainRun(SQLModel, table=True):
    __tablename__ = "train_run"
    id: int | None = Field(default=None, primary_key=True)
    train_id: int = Field(foreign_key="train.id")
    train_run_num_id: int = Field(foreign_key="train_run_num.id")
    running_date: date
    finished: bool = False

    train: "Train" = Relationship(back_populates="train_runs")
    train_run_num: "TrainRunNum" = Relationship(back_populates="train_runs")
    tickets: list["Ticket"] = Relationship(back_populates="train_run")


class Train(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: TrainType
    valid: bool = False
    deprecated: bool = False

    train_runs: list["TrainRun"] = Relationship(back_populates="train")
    carriages: list["Carriage"] = Relationship(back_populates="train", cascade_delete=True)


class Carriage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    train_id: int | None = Field(default=None, foreign_key="train.id")
    num: int
    type: str
    deprecated: bool = False

    train: Train | None = Relationship(back_populates="carriages")
    seats: list["Seat"] = Relationship(back_populates="carriage", cascade_delete=True)


class Seat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    carriage_id: int = Field(foreign_key="carriage.id")
    seat_num: str
    available: bool = True

    carriage: Carriage = Relationship(back_populates="seats")
    tickets: list["Ticket"] = Relationship(back_populates="seat")


class TrainRunNum(SQLModel, table=True):
    __tablename__ = "train_run_num"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    deprecated: bool = False

    train_runs: list["TrainRun"] = Relationship(back_populates="train_run_num")
    routes: list["Route"] = Relationship(back_populates="train_run_num")


class Route(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    train_run_num_id: int = Field(foreign_key="train_run_num.id")
    station_id: int = Field(foreign_key="station.id")
    arrival_time: time
    departure_time: time
    sequence: int

    train_run_num: TrainRunNum = Relationship(back_populates="routes")
    station: "Station" = Relationship(back_populates="routes")


class Station(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    city: str
    deprecated: bool = False

    routes: list["Route"] = Relationship(back_populates="station")




