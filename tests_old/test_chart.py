# Boilerplate
import pytest

from starlight.chart import Chart
from starlight.objects import Angle, Planet


def test_chart_initialization():
    # Example date & location
    birthdate = {"year": 1994, "month": 1, "day": 6, "hour": 19, "minute": 47}
    location = (37.386051, -122.083855)
    chart = Chart(date=birthdate, loc=location, houses="Placidus")

    assert chart.date.year == 1994
    assert chart.loc == location
    # Basic check that planets or angles got instantiated
    assert len(chart.planets) > 0
    assert len(chart.angles) > 0
