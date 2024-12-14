from pydantic import BaseModel
from .models import TrainType, CarriageType

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