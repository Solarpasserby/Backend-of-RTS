from sqlmodel import Session
from . import models

def user_init(session: Session):
    user = models.User(name="admin", password="admin")
    session.add(user)
    session.commit()