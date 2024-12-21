from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from datetime import datetime, date, time
from typing import List

class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class TicketSlotStatus(str, Enum):
    empty = "empty"
    full = "full"
    remaining = "remaining"

class TrainType(str, Enum):
    fast = "fast"
    slow = "slow"

class CarriageType(str, Enum):
    second_class = "second_class"
    first_class = "first_class"
    business = "business"


class Admin(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    password: str


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    telephone: str
    password: str
    banned: bool = False

    orders: List["Order"] = Relationship(back_populates="user")


class TicketSlot(SQLModel, table=True):
    __tablename__ = "ticket_slot"
    id: int | None = Field(default=None, primary_key=True)
    train_run_id: int = Field(foreign_key="train_run.id")
    seat_id: int = Field(foreign_key="seat.id")
    status: TicketSlotStatus

    train_run: "TrainRun" = Relationship(back_populates="ticket_slots")
    seat: "Seat" = Relationship(back_populates="ticket_slots")
    tickets: List["Ticket"] = Relationship(back_populates="ticket_slot", cascade_delete=True)


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ticket_slot_id: int = Field(foreign_key="ticket_slot.id")
    price: float
    sold: bool = False
    used: bool = False
    start_sequence: int
    end_sequence: int

    ticket_slot: TicketSlot = Relationship(back_populates="tickets")
    order: "Order" = Relationship(back_populates="ticket")


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(foreign_key="user.id")
    ticket_id: int | None = Field(foreign_key="ticket.id")
    status: OrderStatus
    created_at: datetime
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None

    user: User | None = Relationship(back_populates="orders")
    ticket: Ticket | None = Relationship(back_populates="order")


class TrainRun(SQLModel, table=True):
    __tablename__ = "train_run"
    id: int | None = Field(default=None, primary_key=True)
    train_id: int = Field(foreign_key="train.id")
    train_run_num_id: int = Field(foreign_key="train_run_num.id")
    running_date: date
    locked: bool = False
    finished: bool = False

    train: "Train" = Relationship(back_populates="train_runs")
    train_run_num: "TrainRunNum" = Relationship(back_populates="train_runs")
    ticket_slots: List["TicketSlot"] = Relationship(back_populates="train_run", cascade_delete=True)


class Train(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: TrainType
    valid: bool = False
    deprecated: bool = False

    train_runs: List["TrainRun"] = Relationship(back_populates="train")
    carriages: List["Carriage"] = Relationship(back_populates="train", cascade_delete=True)


class Carriage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    train_id: int | None = Field(default=None, foreign_key="train.id")
    num: int
    type: str
    deprecated: bool = False

    train: Train | None = Relationship(back_populates="carriages")
    seats: List["Seat"] = Relationship(back_populates="carriage", cascade_delete=True)


class Seat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    carriage_id: int = Field(foreign_key="carriage.id")
    seat_num: str
    available: bool = True

    ticket_slots: List["TicketSlot"] = Relationship(back_populates="seat", cascade_delete=True)
    carriage: Carriage = Relationship(back_populates="seats")


class TrainRunNum(SQLModel, table=True):
    __tablename__ = "train_run_num"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    deprecated: bool = False

    train_runs: List["TrainRun"] = Relationship(back_populates="train_run_num")
    routes: List["Route"] = Relationship(back_populates="train_run_num", cascade_delete=True)


class Route(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    train_run_num_id: int = Field(foreign_key="train_run_num.id")
    station_id: int = Field(foreign_key="station.id")
    arrival_time: time
    departure_time: time
    sequence: int
    kilometers: int

    train_run_num: TrainRunNum = Relationship(back_populates="routes")
    station: "Station" = Relationship(back_populates="routes")


class Station(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    city: str
    deprecated: bool = False

    routes: List["Route"] = Relationship(back_populates="station")




