# Boilerplate
import sys

import pytest

from starlight.usage import geolocator


def test_geolocator_san_francisco():
    # This test might need an internet connection or a local geopy db.
    # You can skip it if offline. Mark with @pytest.mark.skipif condition, if needed.
    city_name = "San Francisco"
    location = geolocator.geocode(city_name)
    assert location is not None
    assert "San Francisco" in location.address
    # Check lat/lon is roughly correct
    assert abs(location.latitude - 37.77) < 1.0
    assert abs(location.longitude + 122.42) < 1.0
    assert abs(location.latitude - 37.77) < 1.0
    assert abs(location.longitude + 122.42) < 1.0
