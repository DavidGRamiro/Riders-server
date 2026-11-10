import os
from pathlib import Path

import polyline
import requests
from dotenv import load_dotenv

from apps.ai.exceptions import RoutePersistenceException

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def engine_route(coords: list):
    try:
        locations = format_coords(coords)
        response = call_valhalla_service(locations)
        return generate_obj(response)
    except Exception as ex:
        raise RoutePersistenceException() from ex


def format_coords(coords: list):
    locations = []
    for index, coord in enumerate(coords):
        if coord.get("msg") is not None:
            continue
        locations.append({
            "lat": float(coord["lat"]),
            "lon": float(coord["lon"]),
            "type": "break" if (index == 0 or index == len(coords) - 1) else "through",
        })
    return locations


def call_valhalla_service(locations: list):
    url_valhalla = os.environ.get("VALHALLA_URL", "localhost")
    payload = {
        "locations": locations,
        "costing": "motorcycle",
        "units": "kilometers",
        "language": "es-ES",
        "shape_format": "polyline6",
        "costing_options": {"motorcycle": {"use_highways": 0.0, "use_trails": 0.9}},
    }
    try:
        response = requests.post(url_valhalla, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as ex:
        raise RoutePersistenceException() from ex


def generate_obj(response):
    trip = response["trip"]
    coordinates = []

    for leg in trip["legs"]:
        points = polyline.decode(leg["shape"], precision=6)

        for lat, lon in points:
            coordinates.append({
                "lat": float(lat),
                "lon": float(lon),
            })

    return {
        "distance": trip["summary"]["length"],
        "duration": trip["summary"]["time"],
        "coordinates": coordinates,
    }
