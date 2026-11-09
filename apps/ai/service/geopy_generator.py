import logging
from geopy import Nominatim

logger = logging.getLogger(__name__)


def create_coordinates(way_points: list):
    """
    Get the complete information for each waypoint using the Nominatim API.

    :param way_points: waypoint names returned by Ollama
    :return: list with the geocoded information of each waypoint; waypoints
        that cannot be geocoded are returned as ``{"position", "msg"}`` entries
    """
    geolocator = Nominatim(user_agent="riders", timeout=10)
    geopy_response = []

    for position in way_points:
        try:
            location = geolocator.geocode(position, language="es")
        except Exception as exc:
            logger.warning("Error geocoding waypoint '%s': %s", position, exc)
            geopy_response.append({"position": position, "msg": "Position not found"})
            continue

        if location is None:
            geopy_response.append({"position": position, "msg": "Position not found"})
            continue

        geopy_response.append({
            "location": location.address,
            "altitude": location.altitude,
            "lat": location.latitude,
            "lon": location.longitude,
            "name": location.raw.get("name"),
        })

    return geopy_response
