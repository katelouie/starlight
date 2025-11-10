# Boilerplate

import pytest

from starlight.signs import Sign, sign_names


def test_sign_list():
    # Basic check
    assert len(sign_names) == 12
    assert "Aries" in sign_names
    assert "Pisces" in sign_names


def test_sign_class():
    s = Sign("Leo")
    assert s.name == "Leo"
    assert s.element == "Fire"
    # Check a property is returning correct info
    assert s.ruler_m == "Sun"  # modern ruler for Leo
    assert s.ruler_m == "Sun"  # modern ruler for Leo
