# Boilerplate
import pytest

from starlight.objects import Angle, Planet


def test_planet_initialization():
    # Example: creating a Planet instance
    p = Planet(name="Mars", swe=4, julian=2451545.0)
    assert p.name == "Mars"
    assert p.swe == 4


def test_planet_is_retro_property():
    # Example: checking retrograde detection
    p = Planet(name="Venus", swe=3, julian=2451545.0)
    # Suppose we forcibly set speed_long negative to simulate retro
    p.speed_long = -0.5
    assert p.is_retro is True


def test_angle_str():
    # Example: verifying Angle string representation
    a = Angle(name="ASC", long=123.456)
    angle_str = str(a)
    assert "ASC" in angle_str
    assert "123.456" in angle_str
    assert "123.456" in angle_str
