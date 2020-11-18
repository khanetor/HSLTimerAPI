from typing import Optional
import time

from fastapi import FastAPI

from location_services import find_coordinate, Address, Coordinate
from hsl_services import get_routes

from routers import hsl_v1

app = FastAPI(
    title="HSL Timer API",
    description="This API searches for up coming nearby bus/tram routes, provided a location.",
    version="1.0")

@app.get("/", tags=["health-check"], description="The time in the response is in UTC milliseconds.")
def read_root():
    return {
        'message': "Welcome to HSL Timer API",
        'currentUTCTime': round(time.time() * 1000)
    }

app.include_router(hsl_v1.router, prefix='/v1', tags=['hsl', 'v1'])
