from typing import Iterable
from pydantic import BaseModel

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from jsonpath_ng import parse

from location_services import Coordinate


transport = AIOHTTPTransport(url='https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql')


class Station(BaseModel):
    name: str
    code: str
    position: Coordinate


class Route(BaseModel):
    name: str
    mode: str
    headsign: str
    arrive_at: int
    stop: Station


async def get_routes(coordinate: Coordinate, radius=500, numDepartures=20) -> Iterable[Route]:

    def parseHSLResponse(json):
        jsonpath_expr = parse('$.stopsByRadius.edges[*].node.stop[*]')
        parsed = jsonpath_expr.find(json)

        for stop in parsed:
            if stop.value['code'] is None:
                continue

            coordinate = Coordinate(lat=stop.value['lat'], lon=stop.value['lon'])
            station = Station(name=stop.value['name'], code=stop.value['code'], position=coordinate)

            for route in stop.value['stoptimesWithoutPatterns']:
                if route['headsign'] is None:
                    continue

                name = route['trip']['route']['shortName']
                mode = route['trip']['route']['mode']
                headsign = route['headsign']
                arrive_at = route['serviceDay'] + route['realtimeArrival']

                route = Route(name=name, mode=mode, headsign=headsign, arrive_at=arrive_at, stop=station)
                yield route

    query = gql(
    """
        query ($numDepartures: Int, $lat: Float!, $lon: Float!, $radius: Int!) {
            stopsByRadius(lat: $lat, lon: $lon, radius: $radius) {
                edges {
                    node {
                        stop {
                            lat
                            lon
                            name
                            code
                            stoptimesWithoutPatterns(numberOfDepartures: $numDepartures) {
                                headsign
                                realtimeArrival
                                serviceDay
                                trip {
                                    route {
                                        shortName
                                        mode
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    """)
    
    params = {
        'numDepartures': numDepartures,
	    'lat': coordinate.lat,
	    'lon': coordinate.lon,
	    'radius': radius
    }

    async with Client(transport=transport, fetch_schema_from_transport=True) as session:
        result = await session.execute(query, variable_values=params)
    
    data = parseHSLResponse(result)
    return data
