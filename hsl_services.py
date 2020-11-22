from typing import Iterable
from dataclasses import dataclass

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from jsonpath_ng import parse

from location_services import Coordinate


transport = AIOHTTPTransport(url='https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql')


@dataclass
class Station:
    name: str
    code: str
    position: Coordinate


@dataclass
class Route:
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
            coordinate = Coordinate(stop.value['lat'], stop.value['lon'])
            station = Station(stop.value['name'], stop.value['code'], coordinate)

            for route in stop.value['stoptimesWithoutPatterns']:
                name = route['trip']['route']['shortName']
                mode = route['trip']['route']['mode']
                headsign = route['headsign']
                arrive_at = route['serviceDay'] + route['realtimeArrival']

                route = Route(name, mode, headsign, arrive_at, station)
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
