import logging
import math
import time
import unicodedata

from geopy import Nominatim

logger = logging.getLogger(__name__)

NOMINATIM_DELAY_SECONDS = 1.0
ENRICH_INTERVAL_KM = 18.0
MAX_ENRICHED_POINTS = 8
ANCHOR_MERGE_RADIUS_KM = 3.0


def _normalize_name(name: str) -> str:
    text = unicodedata.normalize("NFKD", name or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    return text.casefold().strip()


def _point_name(point: dict) -> str:
    return point.get("name") or (point.get("location") or "").split(",")[0].strip()


def _haversine_km(first: dict, second: dict) -> float:
    radius = 6371.0
    lat1 = math.radians(first["lat"])
    lon1 = math.radians(first["lon"])
    lat2 = math.radians(second["lat"])
    lon2 = math.radians(second["lon"])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(value))


def _nearest_route_index(point: dict, route_coordinates: list, start: int = 0) -> int:
    best_index = start
    best_distance = float("inf")
    for index in range(start, len(route_coordinates)):
        distance = _haversine_km(point, route_coordinates[index])
        if distance < best_distance:
            best_distance = distance
            best_index = index
    return best_index


def _reverse_name(location) -> str:
    address = location.raw.get("address") or {}
    for key in ("village", "town", "city", "municipality", "hamlet", "suburb"):
        if address.get(key):
            return address[key]
    return (location.address or "").split(",")[0].strip()


def create_coordinates(way_points: list):
    """
    Get the complete information for each waypoint using the Nominatim API.

    :param way_points: waypoint names returned by Ollama
    :return: list with the geocoded information of each waypoint; waypoints
        that cannot be geocoded are skipped
    """
    geolocator = Nominatim(user_agent="riders", timeout=10)
    geopy_response = []

    for index, position in enumerate(way_points):
        if index:
            time.sleep(NOMINATIM_DELAY_SECONDS)
        try:
            location = geolocator.geocode(position, language="es")
        except Exception as exc:
            logger.warning("Error geocoding waypoint '%s': %s", position, exc)
            continue

        if location is None:
            continue

        geopy_response.append({
            "location": location.address,
            "lat": location.latitude,
            "lon": location.longitude,
            "name": location.raw.get("name"),
        })

    return geopy_response


def enrich_waypoints(anchors: list, route_coordinates: list) -> list:
    """
    Add real intermediate towns along the route returned by Valhalla.

    The model only provides the mandatory anchors (origin, mentioned places and
    destination). This samples the actual route and reverse geocodes it, so the
    intermediate waypoints are real towns that lie on the route corridor.

    :param anchors: geocoded mandatory waypoints
    :param route_coordinates: coordinates of the route returned by Valhalla
    :return: anchors plus intermediate towns, ordered along the route
    """
    if not anchors or not route_coordinates:
        return anchors

    geolocator = Nominatim(user_agent="riders", timeout=10)
    anchor_entries = []
    start_index = 0
    for order, anchor in enumerate(anchors):
        index = _nearest_route_index(anchor, route_coordinates, start_index)
        anchor_entries.append((index, order, anchor, True))
        start_index = index

    samples = []
    travelled = 0.0
    next_mark = ENRICH_INTERVAL_KM
    for index in range(1, len(route_coordinates)):
        travelled += _haversine_km(route_coordinates[index - 1], route_coordinates[index])
        if travelled >= next_mark:
            samples.append((index, route_coordinates[index]))
            next_mark += ENRICH_INTERVAL_KM
            if len(samples) >= MAX_ENRICHED_POINTS:
                break

    enriched_entries = []
    for index, point in samples:
        if any(
            _haversine_km(point, anchor) <= ANCHOR_MERGE_RADIUS_KM
            for anchor in anchors
        ):
            continue

        time.sleep(NOMINATIM_DELAY_SECONDS)
        try:
            location = geolocator.reverse(
                (point["lat"], point["lon"]), language="es", zoom=16
            )
        except Exception as exc:
            logger.warning("Error reverse geocoding route point: %s", exc)
            continue

        if location is None:
            continue

        enriched_entries.append((
            index,
            len(anchor_entries) + len(enriched_entries),
            {
                "location": location.address,
                "lat": point["lat"],
                "lon": point["lon"],
                "name": _reverse_name(location),
            },
            False,
        ))

    seen = {_normalize_name(_point_name(anchor)) for anchor in anchors}
    result = []
    for _, _, point, is_anchor in sorted(
        anchor_entries + enriched_entries, key=lambda entry: (entry[0], entry[1])
    ):
        key = _normalize_name(_point_name(point))
        if not is_anchor:
            if not key or key in seen:
                continue
            seen.add(key)
        result.append(point)

    return result
