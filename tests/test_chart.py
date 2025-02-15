# Boilerplate
import pytest

from starlight.chart import Chart
from starlight.objects import Angle, Planet


def test_chart_initialization():
    # Example date & location
    birthdate = {"year": 1994, "month": 1, "day": 6, "hour": 19, "minute": 47}
    location = (37.386051, -122.083855)
    chart = Chart(birthdate, location, "Placidus")

    assert chart.date.year == 1994
    assert chart.loc == location
    # Basic check that planets or angles got instantiated
    assert len(chart.planets) > 0
    assert len(chart.angles) > 0


def test_calc_arabic_part():
    # If you have a method for Part of Fortune or similar
    birthdate = {"year": 1994, "month": 1, "day": 6, "hour": 19, "minute": 47}
    location = (37.386051, -122.083855)
    chart = Chart(birthdate, location, "Placidus")
    fortuna = chart.calc_arabic_part("fortune")
    # Just check it's a float in valid range
    assert 0 <= fortuna < 360
    assert 0 <= fortuna < 360
