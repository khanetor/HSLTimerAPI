from fastapi import APIRouter
from typing import List

from location_services import find_coordinate, Address, Coordinate
from hsl_services import get_routes
from hsl_services import Route


router = APIRouter()


@router.get("/coordinateFor", response_model=Coordinate)
async def get_coordinate(street: str, city: str, postalCode: str):
    address = Address(street=street, city=city, country='Finland', postalCode=postalCode)
    coordinate = await find_coordinate(address)
    return coordinate


@router.get("/routesForCoordinate", response_model=List[Route])
async def get_routes_for_coordinate(lat: float, lon: float):
    coordinate = Coordinate(lat=lat, lon=lon)
    routes = await get_routes(coordinate)
    return sorted(routes, key=lambda r: r.arrive_at)
    

@router.get("/routesForAddress", response_model=List[Route])
async def get_routes_for_address(street: str, city: str, postalCode: str):
    address = Address(street=street, city=city, country='Finland', postalCode=postalCode)
    coordinate = await find_coordinate(address)
    routes = await get_routes(coordinate)
    return sorted(routes, key=lambda r: r.arrive_at)
