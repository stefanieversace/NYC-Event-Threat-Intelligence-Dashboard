import re

# =========================================================
# KNOWN VENUES (HIGH PRIORITY)
# =========================================================
VENUE_COORDS = {
    "madison square garden": (40.7505, -73.9934),
    "msg": (40.7505, -73.9934),
    "barclays center": (40.6826, -73.9754),
    "radio city": (40.7599, -73.9793),
    "radio city music hall": (40.7599, -73.9793),
    "times square": (40.7580, -73.9855),
    "central park": (40.7829, -73.9654),
    "yankee stadium": (40.8296, -73.9262),
    "citi field": (40.7571, -73.8458),
}

# =========================================================
# BOROUGH / AREA FALLBACK
# =========================================================
AREA_COORDS = {
    "manhattan": (40.7831, -73.9712),
    "brooklyn": (40.6782, -73.9442),
    "queens": (40.7282, -73.7949),
    "bronx": (40.8448, -73.8648),
    "staten island": (40.5795, -74.1502),
}

DEFAULT_COORDS = (40.7128, -74.0060)  # NYC center


# =========================================================
# LOCATION INFERENCE
# =========================================================
def infer_location(text):
    """
    Extracts the most relevant location keyword from text.
    Priority:
    1. Known venues
    2. Boroughs
    3. Default NYC
    """

    if not text:
        return "New York City"

    text = text.lower()

    # Clean text (remove punctuation for matching)
    text = re.sub(r"[^\w\s]", " ", text)

    # 1. Check venues first
    for venue in VENUE_COORDS.keys():
        if venue in text:
            return venue.title()

    # 2. Check boroughs
    for area in AREA_COORDS.keys():
        if area in text:
            return area.title()

    # 3. Default
    return "New York City"


# =========================================================
# COORDINATE LOOKUP
# =========================================================
def get_coordinates(location):
    """
    Converts a location string into coordinates.
    """

    if not location:
        return DEFAULT_COORDS

    location_lower = location.lower()

    # Check venue match
    for venue, coords in VENUE_COORDS.items():
        if venue in location_lower:
            return coords

    # Check area match
    for area, coords in AREA_COORDS.items():
        if area in location_lower:
            return coords

    # Default fallback
    return DEFAULT_COORDS
