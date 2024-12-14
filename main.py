from fastapi import FastAPI
from fastapi.params import Depends
from sql.database import engine, SQLModel
from routers import users, stations, trains, carriages
import uvicorn

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
app = FastAPI()
app.include_router(users.router)
app.include_router(stations.router)
app.include_router(trains.router)
app.include_router(carriages.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

def main():
    create_db_and_tables()
    # --reload flag is used to reload the server when the code changes
    # so it's recommended to use it only in development
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)

if __name__ == "__main__":
    main()