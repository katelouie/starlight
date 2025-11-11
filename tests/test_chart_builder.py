import datetime as dt

import pytest
import pytz

from starlight.core.builder import ChartBuilder
from starlight.core.models import ChartLocation
from starlight.core.native import Native
from starlight.engines.ephemeris import MockEphemerisEngine
from starlight.engines.houses import PlacidusHouses, WholeSignHouses


def test_basic_chart_building():
    """Test basic chart construction."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194, name="SF")
    native = Native(datetime, location)

    chart = (
        ChartBuilder.from_native(native)
        .with_ephemeris(MockEphemerisEngine())
        .calculate()
    )

    assert chart.datetime.utc_datetime == datetime
    assert chart.location.name == "SF"
    assert len(chart.positions) > 0


def test_house_system_swapping():
    """Test that we can easily swap house systems."""
    datetime = dt.datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    location = ChartLocation(latitude=37.7749, longitude=-122.4194)
    native = Native(datetime, location)

    # Placidus
    chart1 = (
        ChartBuilder.from_native(native)
        .with_house_systems([PlacidusHouses()])
        .calculate()
    )

    # Placidus
    chart2 = (
        ChartBuilder.from_native(native)
        .with_house_systems([WholeSignHouses()])
        .calculate()
    )

    assert "Placidus" in chart1.house_systems
    assert "Whole Sign" in chart2.house_systems
    # Cusps should be different
    assert (
        chart1.house_systems["Placidus"].cusps
        != chart2.house_systems["Whole Sign"].cusps
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
