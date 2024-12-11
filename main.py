from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlmodel import Session
from typing import Annotated
from sql.database import engine, SQLModel
from sql import crud
import uvicorn

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

sessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI()
@app.get("/")
async def root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

def main():
    session = Session(engine)
    create_db_and_tables()
    crud.user_init(session)
    session.close()
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)

if __name__ == "__main__":
    main()