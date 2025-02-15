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
