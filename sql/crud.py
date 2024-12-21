from fastapi import HTTPException
from sqlmodel import Session, select, func
from datetime import datetime
from sql.models import User, Train, Carriage, Seat, Station, TrainRunNum, Route, TrainRun, Ticket, TicketSlot, Order, Admin
from sql.schemas import UserCreate, UserUpdate, UserLogin, AdminLogin
from sql.schemas import CarriageCreate, CarriageUpdate
from sql.schemas import StationCreate, StationUpdate
from sql.schemas import TrainCreate, TrainUpdate
from sql.schemas import TrainRunNumCreate, TrainRunNumUpdate, TrainRunDemand
from sql.schemas import RouteUpdate
from sql.schemas import TrainRunCreate, TrainRunUpdate
from sql.schemas import OrderCreate
from sql.schemas import AdminLogin

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
price_multiple_dict = {
    "fast": 0.45,
    "slow": 0.3,
    "second_class": 1,
    "first_class": 2,
    "business": 4
}

# Admin
def authenticate_admin(admin: AdminLogin, session: Session):
    admin = session.exec(select(Admin).where(Admin.name == admin.name, Admin.password == admin.password)).one()
    if admin is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin

def get_count(table: str, session: Session):
    if table == "users":
        count = session.exec(select(func.count(User.id))).one()
    elif table == "orders":
        count = session.exec(select(func.count(Order.id))).one()
    elif table == "trains":
        count = session.exec(select(func.count(Train.id))).one()
    elif table == "stations":
        count = session.exec(select(func.count(Station.id))).one()
    elif table == "runs":
        count = session.exec(select(func.count(TrainRun.id))).one()
    elif table == "nums":
        count = session.exec(select(func.count(TrainRunNum.id))).one()
    else:
        raise HTTPException(status_code=400, detail="Invalid table")
    return {"count": count}


# User CRUD
def get_user(user_id: int, session: Session):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_users(offset: int, limit: int, session: Session):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

def authenticate_user(user: UserLogin, session: Session):
    user = session.exec(select(User).where(User.name == user.name, User.password == user.password)).one()
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
def get_order(order_id: int, session: Session):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

def get_orders(offset: int, limit: int, session: Session):
    orders = session.exec(select(Order).offset(offset).limit(limit)).all()
    return orders

def get_orders_by_user(user_id: int, session: Session):
    orders = session.exec(select(Order).where(Order.user_id == user_id)).all()
    return orders

def add_order(order: OrderCreate, session: Session):
    if order.start_seq >= order.end_seq:
        raise HTTPException(status_code=400, detail="Invalid route sequence")
    if session.get(Route, order.start_route_id) is None:
        raise HTTPException(status_code=404, detail="Start route not found")
    if session.get(Route, order.end_route_id) is None:
        raise HTTPException(status_code=404, detail="End route not found")

    if order.is_through:
        ticket_slot = session.exec(select(TicketSlot).where(TicketSlot.train_run_id == order.train_run_id, TicketSlot.status == "empty")).first()
        if ticket_slot is None:
            raise HTTPException(status_code=400, detail="No available ticket slot")
        ticket = Ticket(price=order.price, start_sequence=order.start_seq, end_sequence=order.end_seq)
        ticket_slot.status = "full"
        ticket.ticket_slot = ticket_slot
    else:
        ticket_slots = session.exec(select(TicketSlot).where(TicketSlot.train_run_id == order.train_run_id, TicketSlot.status == "remaining")).all()
        if not ticket_slots:
            ticket_slot = session.exec(select(TicketSlot).where(TicketSlot.train_run_id == order.train_run_id, TicketSlot.status == "empty")).first()
            if ticket_slot is None:
                raise HTTPException(status_code=400, detail="No available ticket slot")
            else:
                ticket = Ticket(price=order.price, start_sequence=order.start_seq, end_sequence=order.end_seq)
                ticket_slot.status = "remaining"
                ticket.ticket_slot = ticket_slot
        else:
            add_failed = True
            for ticket_slot in ticket_slots:
                addable = True
                total = order.total_routes - (order.end_seq - order.start_seq + 1)
                for ticket in ticket_slot.ticket:
                    if (order.start_seq < ticket.start_sequence < order.end_seq or
                        order.start_seq < ticket.end_sequence < order.end_seq or
                        ticket.start_sequence <= order.start_seq and ticket.end_sequence >= order.end_seq):
                        addable = False
                        break

                    total -= ticket.end_sequence - ticket.start_sequence

                if addable:
                    add_failed = False
                    ticket = Ticket(price=order.price, start_sequence=order.start_seq, end_sequence=order.end_seq)
                    if total == 0:
                        ticket_slot.status = "full"
                    elif total < 0:
                        raise HTTPException(status_code=400, detail="Invalid total routes")
                    ticket.ticket_slot = ticket_slot
                    break

            if add_failed:
                ticket_slot = session.exec(select(TicketSlot).where(TicketSlot.train_run_id == order.train_run_id, TicketSlot.status == "empty")).first()
                if ticket_slot is None:
                    raise HTTPException(status_code=400, detail="No available ticket slot")
                else:
                    ticket = Ticket(price=order.price, start_sequence=order.start_seq, end_sequence=order.end_seq)
                    ticket_slot.status = "remaining"
                    ticket.ticket_slot = ticket_slot

    user = session.get(User, order.user_id)
    db_order = Order(status="pending", created_at=datetime.now())
    db_order.user = user
    db_order.ticket = ticket

    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order

def complete_order(order_id: int, session: Session):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Invalid order status")
    order.status = "completed"
    order.completed_at = datetime.now()
    order.ticket.sold = True
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def cancel_order(order_id: int, session: Session):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == "cancelled":
        return {"message": "Order already cancelled"}
    order.status = "cancelled"
    order.cancelled_at = datetime.now()

    ticket = order.ticket
    ticket_slot = session.get(TicketSlot, ticket.ticket_slot_id)
    if ticket_slot is None:
        raise HTTPException(status_code=404, detail="Ticket slot not found")
    if len(ticket_slot.tickets) == 1:
        ticket_slot.status = "empty"
    elif len(ticket_slot.tickets) > 1:
        ticket_slot.status = "remaining"
    session.delete(ticket)
    session.add(ticket_slot)

    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def remove_order(order_id: int, session: Session):
    order = session.get(Order, order_id)
    ticket = session.get(Ticket, order.ticket_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    ticket_slot = session.get(TicketSlot, ticket.ticket_slot_id)
    if ticket_slot is None:
        raise HTTPException(status_code=404, detail="Ticket slot not found")
    if len(ticket_slot.ticket) == 1:
        ticket_slot.status = "empty"
    elif len(ticket_slot.ticket) > 1:
        ticket_slot.status = "remaining"
    session.delete(order)
    session.delete(ticket)
    session.add(ticket_slot)
    session.commit()
    return {"message": "Order deleted successfully"}

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

    row_seats = seat_dict[carriage.type]
    for i in range(seat_rows):
        for j in range(row_seats):
            num = f"{i+1}{seat_num_dict[carriage.type][j]}"
            seat = Seat(seat_num=num)
            db_carriage.seats.append(seat)

    session.add(db_carriage)


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
        carriage_type = session.get(Carriage, carriage_id).type
        if carriage_type not in train_dict[train.type]:
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

def get_trains(offset: int, limit: int, session: Session):
    trains = session.exec(select(Train).offset(offset).limit(limit)).all()
    return trains

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

def get_stations(offset: int, limit: int, session: Session):
    stations = session.exec(select(Station).offset(offset).limit(limit)).all()
    return stations

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

def get_train_run_nums(offset: int, limit: int, session: Session):
    train_run_nums = session.exec(select(TrainRunNum).offset(offset).limit(limit)).all()
    return train_run_nums

def add_train_run_num(train_run_num: TrainRunNumCreate, session: Session):
    train_run_num_data = train_run_num.model_dump()
    train_run_num_data.pop("routes")
    db_train_run_num = TrainRunNum.model_validate(train_run_num_data)
    session.add(db_train_run_num)

    i = 1
    kilometers = 0
    for route in train_run_num.routes:
        if route.sequence != i:
            raise HTTPException(status_code=400, detail="Invalid sequence")
        if route.kilometers < kilometers:
            raise HTTPException(status_code=400, detail="Invalid kilometers")
        i += 1
        kilometers = route.kilometers

        route_data = route.model_dump()
        station_name = route_data.pop("station_name")
        station = session.exec(select(Station).where(Station.name == station_name)).first()
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

def get_train_runs(offset: int, limit: int, session: Session):
    train_runs = session.exec(select(TrainRun).offset(offset).limit(limit)).all()
    return train_runs


def get_train_runs_by_demand(train_run_demand: TrainRunDemand, session: Session):
    # 获取起点和终点站点信息
    stations = session.exec(
        select(Station)
        .where(Station.name.in_([train_run_demand.start_station, train_run_demand.end_station]))
    ).all()

    if len(stations) != 2:
        missing_stations = [name for name in [train_run_demand.start_station, train_run_demand.end_station]
                            if not any(station.name == name for station in stations)]
        raise HTTPException(status_code=404, detail=f"Stations not found: {', '.join(missing_stations)}")

    # 提取起点和终点站点
    station_map = {station.name: station for station in stations}
    start_station = station_map[train_run_demand.start_station]
    end_station = station_map[train_run_demand.end_station]

    # 子查询：获取 Route.sequence 的值
    start_station_sequence = (
        select(Route.sequence)
        .where(
            Route.station_id == start_station.id,
            Route.train_run_num_id == TrainRunNum.id
        )
    ).scalar_subquery()

    end_station_sequence = (
        select(Route.sequence)
        .where(
            Route.station_id == end_station.id,
            Route.train_run_num_id == TrainRunNum.id
        )
    ).scalar_subquery()

    # 主查询
    train_runs = session.exec(
        select(TrainRun)
        .join(TrainRunNum)
        .where(
            TrainRunNum.deprecated == False,
            TrainRunNum.routes.any(
                Route.station_id.in_([start_station.id, end_station.id])
            ),
            TrainRun.locked == True,
            TrainRun.finished == False,
            TrainRun.running_date == train_run_demand.running_date,
            start_station_sequence < end_station_sequence  # 起点序号需小于终点序号
        )
    ).all()

    return train_runs

def add_train_run(train_run: TrainRunCreate, session: Session):
    train = session.get(Train, train_run.train_id)
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    if not train.valid:
        raise HTTPException(status_code=400, detail="The train is not valid")
    train_run_num = session.get(TrainRunNum, train_run.train_run_num_id)
    if train_run_num is None:
        raise HTTPException(status_code=404, detail="TrainRunNum not found")

    db_train_run = TrainRun.model_validate(train_run)
    db_train_run.train = train
    db_train_run.train_run_num = train_run_num

    for carriage_id in session.exec(select(Carriage.id).where(Carriage.train_id == train.id)):
        for seat in session.exec(select(Seat).where(Seat.carriage_id == carriage_id)):
            ticket_slot = TicketSlot(status="empty")
            ticket_slot.seat = seat
            db_train_run.ticket_slots.append(ticket_slot)

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
    if train_run.locked:
        raise HTTPException(status_code=400, detail="You can't delete locked train run")
    session.delete(train_run)
    session.commit()
    return {"message": "TrainRun deleted successfully"}

def modify_train_run(train_run_id: int, train_run: TrainRunUpdate, session: Session):
    db_train_run = session.get(TrainRun, train_run_id)
    if db_train_run is None:
        raise HTTPException(status_code=404, detail="TrainRun not found")
    if db_train_run.locked:
        raise HTTPException(status_code=400, detail="You can't modify locked train run")

    train_run_data = train_run.model_dump(exclude_unset=True)
    db_train_run.sqlmodel_update(train_run_data)
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