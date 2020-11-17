from typing import Optional

from fastapi import FastAPI

from location_services import find_coordinate, Address, Coordinate
from hsl_services import get_routes

from routers import hsl_v1

app = FastAPI(title="HSL Timer API")

@app.get("/")
def read_root():
    return {
        'message': "Welcome to HSL Timer API"
    }

app.include_router(hsl_v1.router, prefix='/v1', tags=['hsl', 'v1'])
