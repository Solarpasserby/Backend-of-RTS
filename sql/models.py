from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime, date

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
    economy = "economy"
    business = "business"
    first_class = "first_class"

class SeatStatus(str, Enum):
    available = "available"
    booked = "booked"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    telephone: str
    password: str

    orders: list["Order"] = Relationship(back_populates="user")


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    ticket_id: int = Field(foreign_key="ticket.id")
    status: OrderStatus
    created_at: datetime
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None

    user: User = Relationship(back_populates="orders")
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
    id: int | None = Field(default=None, primary_key=True)
    train_id: int = Field(foreign_key="train.id")
    train_run_num_id: int = Field(foreign_key="train_run_num.id")
    running_date: date

    train: "Train" = Relationship(back_populates="train_runs")
    train_run_num: "TrainRunNum" = Relationship(back_populates="train_runs")
    tickets: list["Ticket"] = Relationship(back_populates="train_run")


class Train(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: TrainType

    train_runs: list["TrainRun"] = Relationship(back_populates="train")
    carriages: list["Carriage"] = Relationship(back_populates="train")


class Carriage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    train_id: int = Field(foreign_key="train.id")
    num: int
    type: str

    train: "Train" = Relationship(back_populates="carriages")
    seats: list["Seat"] = Relationship(back_populates="carriage")


class Seat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    carriage_id: int = Field(foreign_key="carriage.id")
    seat_num: int
    status: SeatStatus

    carriage: Carriage = Relationship(back_populates="seats")
    tickets: list["Ticket"] = Relationship(back_populates="seat")


class TrainRunNum(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str

    train_runs: list["TrainRun"] = Relationship(back_populates="train_run_num")
    routes: list["Route"] = Relationship(back_populates="train_run_num")


class Route(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    train_run_num_id: int = Field(foreign_key="train_run_num.id")
    station_id: int = Field(foreign_key="station.id")
    arrival_time: datetime
    departure_time: datetime
    sequence: int

    train_run_num: TrainRunNum = Relationship(back_populates="routes")
    station: "Station" = Relationship(back_populates="routes")


class Station(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    city: str

    routes: list["Route"] = Relationship(back_populates="station")




