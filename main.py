from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sql.database import engine, SQLModel
from routers import users, stations, trains, carriages, trainrunnums, trainruns, orders, admin
import uvicorn

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
app = FastAPI(root_path="/api")
app.include_router(users.router)
app.include_router(stations.router)
app.include_router(trains.router)
app.include_router(carriages.router)
app.include_router(trainrunnums.router)
app.include_router(trainruns.router)
app.include_router(orders.router)
app.include_router(admin.router)

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:443",
    "https://lorenash.me",
    "https://lorenash.me:443",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

def main():
    create_db_and_tables()
    uvicorn.run("main:app", host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()