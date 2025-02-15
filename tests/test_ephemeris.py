# Boilerplate
import pytest
import swisseph as swe

from starlight.ephemeris import calc_julian, calc_planet_pos


def test_calc_julian():
    # Basic test for Julian day calculation
    isvalid, jd, dt = calc_julian(2000, 1, 1, 12, 0)
    assert isvalid == 0  # 0 usually means success in swisseph date_conversion
    # Known value for 2000-01-01 12:00 UT is ~ 2451545.0
    assert abs(jd - 2451545.0) < 0.5


def test_calc_planet_pos():
    # Testing a planet's position on a known date
    # For example, let's pick Sun (swe.SUN=0)
    isvalid, jd, dt = calc_julian(2000, 1, 1, 12, 0)
    result = calc_planet_pos(jd, swe.SUN)
    assert "long" in result
    assert "lat" in result
    assert "sign" in result
    # Check sign is something expected (Sun in Capricorn around Jan 1)
    assert result["sign"] in ["Capricorn", "Sagittarius", "Aquarius"]
    assert result["sign"] in ["Capricorn", "Sagittarius", "Aquarius"]
