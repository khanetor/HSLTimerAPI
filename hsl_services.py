from typing import List
from dataclasses import dataclass

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from jsonpath_ng import parse

from location_services import Coordinate


transport = AIOHTTPTransport(url='https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql')


@dataclass
class Route:
    name: str
    mode: str
    head_sign: str
    arrive_at: int


async def get_routes(coordinate: Coordinate, radius=500, numDepartures=2) -> List[Route]:

    def parseHSLResponse(json):
        jsonpath_expr = parse('$.stopsByRadius.edges[*].node.stop[*].stoptimesWithoutPatterns')
        parsed = jsonpath_expr.find(json)

        for stop in parsed:
            for route in stop.value:
                name = route['trip']['route']['shortName']
                mode = route['trip']['route']['mode']
                head_sign = route['headsign']
                arrive_at = route['serviceDay'] + route['realtimeArrival']

                route = Route(name, mode, head_sign, arrive_at)
                yield route

    query = gql(
    """
        query ($numDepartures: Int, $lat: Float!, $lon: Float!, $radius: Int!) {
            stopsByRadius(lat: $lat, lon: $lon, radius: $radius) {
                edges {
                    node {
                        stop {
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
