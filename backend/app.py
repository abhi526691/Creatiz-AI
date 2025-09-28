from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import contentGenerator

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}

app.include_router(contentGenerator.router)

