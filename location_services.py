import httpx
from dataclasses import dataclass


@dataclass
class Address:
    street: str
    city: str
    country: str
    postalCode: str

@dataclass
class Coordinate:
    lat: float
    lon: float


async def find_coordinate(address: Address) -> Coordinate:
    street = address.street
    city = address.city
    country = address.country
    postalCode = address.postalCode

    url = "https://nominatim.openstreetmap.org/search?street=%s&city=%s&country=%s&postalcode=%s&format=json" % (street, city, country, postalCode)
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
    
    if resp.status_code == 200:
        data = resp.json()
        if len(data) == 0:
            raise "Cannot find coordinate"
        location = data[0]
        lat = location['lat']
        lon = location['lon']
        return Coordinate(lat, lon)
    else:
        raise "Error while looking up coordinate"

