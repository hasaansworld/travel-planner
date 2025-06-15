from fastapi import FastAPI
from datetime import datetime
import click

app = FastAPI(
    title="Travel Planner",
    description="A travel planner app backend",
)

@app.get("/")
async def root():
    return "Hello World! This is a travel planner"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)