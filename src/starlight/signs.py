"""Setting up Signs objects."""

sign_names = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

rulers = [
    {"trad": "Mars", "modern": "Mars"},
    {"trad": "Venus", "modern": "Venus"},
    {"trad": "Mercury", "modern": "Mercury"},
    {"trad": "Moon", "modern": "Moon"},
    {"trad": "Sun", "modern": "Sun"},
    {"trad": "Mercury", "modern": "Mercury"},
    {"trad": "Venus", "modern": "Venus"},
    {"trad": "Mars", "modern": "Pluto"},
    {"trad": "Jupiter", "modern": "Jupiter"},
    {"trad": "Saturn", "modern": "Saturn"},
    {"trad": "Saturn", "modern": "Uranus"},
    {"trad": "Jupiter", "modern": "Neptune"},
]

dignities_planet = {
    "Sun": {
        "ruler_traditional": "Leo",
        "ruler_modern": "Leo",
        "exhalted": "Aries",
        "detriment": "Aquarius",
        "fall": "Libra"
    }
}

DIGNITIES = {
    "Aries": {
        "symbol": "♈︎",
        "exhalt_degree": 19,
        "traditional": {
            "ruler": "Mars",
            "exhalt": "Sun",
            "detriment": "Venus",
            "fall": "Saturn"
        },
        "modern": {
            "ruler": "Mars",
            "exhalt": "Sun",
            "detriment": "Venus",
            "fall": "Saturn"
        },
        "decan_trip": ["Mars", "Sun", "Jupiter"],
        "decan_chaldean": ["Mars", "Sun", "Venus"],
        "bound_egypt": { # key is start of the planet's domicile degrees.
            0: "Jupiter",
            6: "Venus",
            12: "Mercury",
            20: "Mars",
            25: "Saturn",
        },
        "triplicity": {
            "day": "Sun",
            "night": "Jupiter",
            "coop": "Saturn"
        }
    },
"Taurus": {
        "symbol": "♉︎",
        "exhalt_degree": 3,
        "traditional": {
            "ruler": "Venus",
            "exhalt": "Moon",
            "detriment": "Mars",
            "fall": None,
        },
        "modern": {
            "ruler": "Venus",
            "exhalt": "Moon",
            "detriment": "Pluto",
            "fall": "Uranus"
        },
        "decan_trip": ["Venus", "Mercury", "Saturn"],
        "decan_chaldean": ["Mecury", "Moon", "Saturn"],
        "bound_egypt": { # key is start of the planet's domicile degrees.
            0: "Venus",
            8: "Mercury",
            14: "Jupiter",
            22: "Saturn",
            27: "Mars"
        },
        "triplicity": {
            "day": "Venus",
            "night": "Moon",
            "coop": "Mars"
        }
    },
"Gemini": {
        "symbol": "♊︎",
        "exhalt_degree": 3,
        "traditional": {
            "ruler": "Mercury",
            "exhalt": "North Node",
            "detriment": "Jupiter",
            "fall": "South Node"
        },
        "modern": {
            "ruler": "Mercury",
            "exhalt": "Mercury",
            "detriment": "Jupiter",
            "fall": "Venus"
        },
        "decan_trip": ["Mercury", "Venus", "Saturn"],
        "decan_chaldean": ["Jupiter", "Mars", "Sun"],
        "bound_egypt": { # key is start of the planet's domicile degrees.
            0: "Mercury",
            6: "Jupiter",
            12: "Venus",
            17: "Mars",
            24: "Saturn",
        },
        "triplicity": {
            "day": "Saturn",
            "night": "Mercury",
            "coop": "Jupiter"
        }
    },
    "Cancer": {
        "symbol": "♋︎",
        "exhalt_degree": 15,
        "traditional": {
            "ruler": "Moon",
            "exhalt": "Jupiter",
            "detriment": "Saturn",
            "fall": "Mars"
        },
        "modern": {
            "ruler": "Moon",
            "exhalt": "Jupiter",
            "detriment": "Saturn",
            "fall": "Pluto"
        },
        "decan_trip": ["Moon", "Mars", "Jupiter"],
        "decan_chaldean": ["Venus", "Mercury", "Moon"],
        "bound_egypt": {
            0: "Mars",
            7: "Venus",
            13: "Mercury",
            19: "Jupiter",
            26: "Saturn",
        },
        "triplicity": {
            "day": "Mars",
            "night": "Venus",
            "coop": "Moon"
        }
    },
    "Leo": {
        "symbol": "♌︎",
        "exhalt_degree": None,
        "traditional": {
            "ruler": "Sun",
            "exhalt": "None",
            "detriment": "Saturn",
            "fall": "None"
        },
        "modern": {
            "ruler": "Sun",
            "exhalt": "Neptune",
            "detriment": "Uranus",
            "fall": "Pluto"
        },
        "decan_trip": ["Sun", "Jupiter", "Mars"],
        "decan_chaldean": ["Saturn", "Jupiter", "Mars"],
        "bound_egypt": {
            0: "Jupiter",
            6: "Venus",
            11: "Saturn",
            18: "Mercury",
            24: "Mars",
        },
        "triplicity": {
            "day": "Sun",
            "night": "Jupiter",
            "coop": "Saturn"
        }
    },
    "Virgo": {
        "symbol": "♍︎",
        "exhalt_degree": 15,
        "traditional": {
            "ruler": "Mercury",
            "exhalt": "Mercury",
            "detriment": "Jupiter",
            "fall": "Venus"
        },
        "modern": {
            "ruler": "Mercury",
            "exhalt": "Mercury",
            "detriment": "Neptune",
            "fall": "Venus"
        },
        "decan_trip": ["Mercury", "Saturn", "Venus"],
        "decan_chaldean": ["Sun", "Venus", "Mercury"],
        "bound_egypt": {
            0: "Mercury",
            7: "Venus",
            17: "Jupiter",
            21: "Mars",
            28: "Saturn",
        },
        "triplicity": {
            "day": "Venus",
            "night": "Moon",
            "coop": "Mars"
        }
    },
    "Libra": {
        "symbol": "♎︎",
        "exhalt_degree": 21,
        "traditional": {
            "ruler": "Venus",
            "exhalt": "Saturn",
            "detriment": "Mars",
            "fall": "Sun"
        },
        "modern": {
            "ruler": "Venus",
            "exhalt": "Saturn",
            "detriment": "Mars",
            "fall": "Sun"
        },
        "decan_trip": ["Venus", "Saturn", "Jupiter"],
        "decan_chaldean": ["Moon", "Saturn", "Jupiter"],
        "bound_egypt": {
            0: "Saturn",
            6: "Mercury",
            14: "Jupiter",
            21: "Venus",
            28: "Mars",
        },
        "triplicity": {
            "day": "Saturn",
            "night": "Mercury",
            "coop": "Jupiter"
        }
    },
    "Scorpio": {
        "symbol": "♏︎",
        "exhalt_degree": None,
        "traditional": {
            "ruler": "Mars",
            "exhalt": "None",
            "detriment": "Venus",
            "fall": "Moon"
        },
        "modern": {
            "ruler": "Pluto",
            "exhalt": "Uranus",
            "detriment": "Venus",
            "fall": "Moon"
        },
        "decan_trip": ["Mars", "Sun", "Venus"],
        "decan_chaldean": ["Mars", "Sun", "Venus"],
        "bound_egypt": {
            0: "Mars",
            7: "Venus",
            11: "Mercury",
            19: "Jupiter",
            24: "Saturn",
        },
        "triplicity": {
            "day": "Mars",
            "night": "Venus",
            "coop": "Moon"
        }
    },
    "Sagittarius": {
        "symbol": "♐︎",
        "exhalt_degree": 3,
        "traditional": {
            "ruler": "Jupiter",
            "exhalt": "South Node",
            "detriment": "Mercury",
            "fall": "North Node"
        },
        "modern": {
            "ruler": "Jupiter",
            "exhalt": "Venus",
            "detriment": "Mercury",
            "fall": "Ceres"
        },
        "decan_trip": ["Jupiter", "Mars", "Sun"],
        "decan_chaldean": ["Mercury", "Moon", "Saturn"],
        "bound_egypt": {
            0: "Jupiter",
            12: "Venus",
            17: "Mercury",
            21: "Mars",
            26: "Saturn",
        },
        "triplicity": {
            "day": "Sun",
            "night": "Jupiter",
            "coop": "Saturn"
        }
    },
    "Capricorn": {
        "symbol": "♑︎",
        "exhalt_degree": 27,
        "traditional": {
            "ruler": "Saturn",
            "exhalt": "Mars",
            "detriment": "Moon",
            "fall": "Jupiter"
        },
        "modern": {
            "ruler": "Saturn",
            "exhalt": "Mars",
            "detriment": "Moon",
            "fall": "Jupiter"
        },
        "decan_trip": ["Saturn", "Venus", "Mercury"],
        "decan_chaldean": ["Jupiter", "Mars", "Sun"],
        "bound_egypt": {
            0: "Mercury",
            7: "Jupiter",
            14: "Venus",
            22: "Saturn",
            26: "Mars",
        },
        "triplicity": {
            "day": "Venus",
            "night": "Moon",
            "coop": "Mars"
        }
    },
    "Aquarius": {
        "symbol": "♒︎",
        "exhalt_degree": None,
        "traditional": {
            "ruler": "Saturn",
            "exhalt": "None",
            "detriment": "Sun",
            "fall": "None"
        },
        "modern": {
            "ruler": "Uranus",
            "exhalt": "Pluto",
            "detriment": "Sun",
            "fall": "Neptune"
        },
        "decan_trip": ["Saturn", "Mercury", "Venus"],
        "decan_chaldean": ["Mars", "Sun", "Venus"],
        "bound_egypt": {
            0: "Mercury",
            7: "Venus",
            13: "Jupiter",
            20: "Saturn",
            25: "Mars",
        },
        "triplicity": {
            "day": "Saturn",
            "night": "Mercury",
            "coop": "Jupiter"
        }
    },
    "Pisces": {
        "symbol": "♓︎",
        "exhalt_degree": 27,
        "traditional": {
            "ruler": "Jupiter",
            "exhalt": "Venus",
            "detriment": "Mercury",
            "fall": "Ceres"
        },
        "modern": {
            "ruler": "Neptune",
            "exhalt": "Venus",
            "detriment": "Mercury",
            "fall": "Ceres"
        },
        "decan_trip": ["Jupiter", "Mars", "Moon"],
        "decan_chaldean": ["Saturn", "Jupiter", "Mars"],
        "bound_egypt": {
            0: "Venus",
            12: "Jupiter",
            16: "Mercury",
            19: "Mars",
            28: "Saturn",
        },
        "triplicity": {
            "day": "Mars",
            "night": "Venus",
            "coop": "Moon"
        }
    },
}

# Aries starts a 0 degrees
# Each sign goes to start + 29.9999 (etc) degrees

elements = ["Fire", "Earth", "Air", "Water"]
cardinalities = ["Cardinal", "Fixed", "Mutable"]
humours = ["Choleric", "Sanguine", "Phlegmatic", "Melancholic"]
decans_chald = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
rulers = dict(zip(sign_names, rulers))


class Sign:
    # Zodiac sign

    def __init__(self, name: str, signs: list[str] = sign_names) -> None:
        self.name = name
        self.index = signs.index(name)

    @property
    def element(self, elements: list[str] = elements) -> str:
        return elements[self.index % len(elements)]

    @property
    def ruler(self, rulers=rulers) -> str:
        return rulers[self.name]["modern"]

    @property
    def ruler_t(self, rulers=rulers) -> str:
        return rulers[self.name]["trad"]

    @property
    def ruler_m(self, rulers=rulers) -> str:
        return rulers[self.name]["modern"]

    @property
    def cardinality(self, cardinalities: list[str] = cardinalities) -> str:
        return cardinalities[self.index % len(cardinalities)]

    @property
    def humour(self, humours: list[str] = humours) -> str:
        return humours[self.index % len(humours)]

    @property
    def hemisphere(self) -> str:
        if self.index < 6:
            return "Lower"

        return "Upper"

    @property
    def octave(self) -> int:
        return int(self.index % 4) + 1

    @property
    def quadrant(self) -> int:
        return int(self.index % 3) + 1

    @property
    def house(self) -> int:
        # The house number this sign naturally correlates to
        return self.index + 1

    @property
    def polarity(self) -> str:
        values = ["Positive", "Negative"]

        return values[self.index % 2]

    @property
    def gender(self) -> str:
        values = ["Masculine", "Feminine"]

        return values[self.index % 2]

    @property
    def decan1(self) -> str:
        ...
