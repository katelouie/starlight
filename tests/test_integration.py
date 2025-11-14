"""Integration tests for complete chart calculation."""

import datetime as dt

import pytest

from starlight.core.builder import ChartBuilder
from starlight.core.models import ChartLocation
from starlight.core.native import Native
from starlight.engines.aspects import ModernAspectEngine
from starlight.engines.houses import PlacidusHouses, WholeSignHouses


def test_einstein_chart():
    """Test calculating Einstein's birth chart."""
    birthday = dt.datetime(1879, 3, 14, 11, 30)
    location = "Ulm, Germany"
    native = Native(birthday, location)

    chart = (
        ChartBuilder.from_native(native)
        .with_house_systems([PlacidusHouses()])
        .with_aspects(ModernAspectEngine())
        .calculate()
    )

    # Verify chart was calculated
    assert chart.datetime.local_datetime == birthday
    assert "Ulm" in chart.location.name

    # Verify positions
    assert len(chart.positions) > 10

    # Sun should be Pisces
    sun = chart.get_object("Sun")
    assert sun is not None
    assert sun.sign == "Pisces"

    # Verify houses
    assert chart.default_house_system == "Placidus"
    assert len(chart.house_systems["Placidus"].cusps) == 12

    # Verify aspects calculated
    assert len(chart.aspects) > 0


def test_chart_to_dict():
    """Test chart seralization to dictionary."""
    birthday = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0, name="Test")
    native = Native(birthday, location)

    chart = ChartBuilder.from_native(native).calculate()
    data = chart.to_dict()

    assert "datetime" in data
    assert "location" in data
    assert "positions" in data
    assert "house_systems" in data

    # Verify structure
    assert data["location"]["name"] == "Test"
    assert len(data["positions"]) > 0
    assert len(data["house_systems"]["Placidus"]) == 12


def test_different_house_systems():
    """Test that different house systems product different results."""
    birthday = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=40, longitude=-74)
    native = Native(birthday, location)

    chart = (
        ChartBuilder.from_native(native)
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .calculate()
    )

    # Different systems, different cusps
    assert chart.house_systems["Placidus"] != chart.house_systems["Whole Sign"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
