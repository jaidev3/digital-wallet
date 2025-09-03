from database import create_db_and_tables
import uvicorn
from fastapi import FastAPI
from routers import router as api_router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    await create_db_and_tables()

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
