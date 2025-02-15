# Get ephemeris data for a date + time + location

import calendar as cal
<<<<<<< HEAD
from enum import Flag
import os
import pprint
=======
import os
import pprint
from enum import Flag
>>>>>>> master

import swisseph as swe

from starlight import signs


def set_ephe_path():
    PATH_LIB = os.path.dirname(__file__) + os.sep
    PATH_DATA = PATH_LIB + "data" + os.sep

    swe.set_ephe_path(PATH_DATA + "swisseph" + os.sep + "ephe" + os.sep)


def calc_julian(year, month, day, hour, minute):
    hour_decimal = minute / 60
    isvalid, jd, dt = swe.date_conversion(year, month, day, hour + hour_decimal)

    return isvalid, jd, dt


def convert_lat_to_sign(lat: float, degrees: bool = True) -> str:
    # get sign
    sign = signs.sign_names[int(lat // 30)]
    # get angle of sign
    sign_angle = lat % 30
    sign_minutes = (lat % 1) * 60
    sign_seconds = (sign_minutes % 1) * 60

    if degrees:
        return (
            "%s %2.0f°%2.0f'%2.0f" % (sign, sign_angle, sign_minutes, sign_seconds)
            + '"'
        )

    return sign


def calc_houses(jd, lat: float, long: float, hsys=b"P") -> dict[str, dict]:
    cusps, angles = swe.houses(jd, lat, long, hsys=hsys)

    cusp_d = {index + 1: x for index, x in enumerate(cusps)}
    angle_labels = [
        "ASC",
        "MC",
        "ARMC",
        "VERTEX",
        "EQUASC",
        "COASC1",
        "COASC2",
        "POLASC",
        "NASCMC",
    ]
    angle_d = dict(zip(angle_labels, angles))

    return {"cusp": cusp_d, "angle": angle_d}


def calc_planet_pos(jd, planet, flag=swe.FLG_SPEED, is_planet: bool = True):
    if is_planet:
<<<<<<< HEAD
        xx: tuple, flgret: Flag() = swe.calc_ut(jd, planet, flag)
=======
        xx, flgret = swe.calc_ut(jd, planet, flag)
>>>>>>> master
        planet_name: str = swe.get_planet_name(planet)

        labels = ["long", "lat", "dist", "speed long", "speed declin", "speed dist"]

        result: dict[str, str | float | bool] = dict(zip(labels, xx))
        result["name"] = planet_name

        result["retro"] = result["speed long"] < 0
    else:
        result: dict[str, str | float | bool] = planet

    result["sign"] = signs.sign_names[int(result["long"] // 30)]
    result["sign_deg"] = int(result["long"] % 30)

    minutes_raw = (result["long"] % 1) * 60
    result["sign_min"] = int(minutes_raw)
    result["sign_sec"] = int((minutes_raw % 1) * 60)

    return result


def get_planets(jd, range_tup, flag=swe.FLG_SPEED):
    planets = {}

    for planet in range(*range_tup):
        if planet != swe.EARTH:
            planet_pos = calc_planet_pos(jd, planet, flag=flag)
            planets[planet_pos["name"]] = planet_pos

    return planets


def calc_conjunct(planet1, planet2, orb):
    long1 = planet1["long"]
    long2 = planet2["long"]

    dist_1_to_2 = long2 - long1
    distance = abs(dist_1_to_2)

    is_aspect = distance <= orb
    aspect_orb = distance if is_aspect else None

    return is_aspect, aspect_orb


def calc_aspect(planet1, planet2, degrees, orb):
<<<<<<< HEAD
    long1 = planet1["long"]
    long2 = planet2["long"]
=======
    long1 = planet1.long
    long2 = planet2.long
>>>>>>> master

    dist_1_to_2 = long2 - long1
    dist_2_to_1 = long1 - long2
    distance = abs(dist_1_to_2)

    is_aspect = abs(distance - degrees) <= orb
    aspect_orb = abs(distance - degrees) if is_aspect else None

    if "speed long" in planet1 and "speed long" in planet2:
        if dist_1_to_2 > 0:  # p2 farther than p1
            if planet2["speed long"] > planet1["speed long"]:  # p2 moving faster
                movement = "separating"
            else:
                movement = "applying"
        elif dist_2_to_1 > 0:  # p1 farther than p2
            if planet1["speed long"] > planet2["speed long"]:  # p1 moving faster
                movement = "separating"
            else:
                movement = "applying"
        else:
            movement = None
    else:
        movement = None

    return is_aspect, aspect_orb, distance, movement


def calc_midpoint(planet1, planet2):
    return (planet1["long"] + planet2["long"]) / 2


def calc_arabic_part(part_name, planets, angles):
    if part_name.lower() == "fortune":
        return angles["ASC"] + planets["Sun"]["long"] - planets["Moon"]["long"]
    else:
        return None


def calc_midpoints(objects, pairs) -> dict:
    # returns dict of dicts of form:: obj1-obj2: {long: value}
    midpoints: dict = {}
    for pair in pairs:  # list of tuples
        midpoints[f"{pair[0]}-{pair[1]}"] = {
            "long": calc_midpoint(objects[pair[0]], objects[pair[1]])
        }

    return midpoints


def print_date(year, month, day, hour, minute):
    print(
        f"Date: {cal.month_name[month]} {day} {year} at {hour}:{minute} Universal Time"
    )


def print_planets(planets, houses):
    print(
        "Name\t\tLongitude\tLatitude\tDistance\tSpeed (Long)\t"
        "Speed (Decl)\tSpeed (Dist)\tSign\t\tDegrees\t Rx"
        "\tHouse\tDecan"
    )

    for k, v in planets.items():
        justify = "\t" if len(k) > 8 else "\t\t"
        just_sign = "\t" if len(v["sign"]) >= 8 else "\t\t"

        def __house_pos(planet_long, house_dict):
            house = None

            for k, v in house_dict.items():
                if house is None:
                    house = k

                if planet_long == v:
                    return k + 1
                elif planet_long > v:
                    house = k
                else:
                    return house

            return 12

        print(
            f"{k.title()}{justify}{v['long']:.7f}\t{v['lat']:.7f}\t{v['dist']:.7f}"
            f"\t{v['speed long']:.7f}\t{v['speed declin']:.7f}\t{v['speed dist']:.7f}"
            f"\t{v['sign']}{just_sign}{v['sign_deg']:2.0f}°{v['sign_min']:2.0f}'{v['sign_sec']:2.0f}"
            f'" {"R" if v["retro"] else ""}'
            f"\t{__house_pos(v['long'], houses['cusp'])}\t{v['sign_deg'] // 10 + 1}"
        )


def print_houses(houses):
    print("House Cusp\tLongitude\tSign and Degree")
    for k, v in houses["cusp"].items():
        just = "\t" if k >= 10 else "\t\t"
        print(
            "House " + str(k) + just + str(round(v, 7)) + " \t" + convert_lat_to_sign(v)
        )


def print_angles(houses):
    print("Chart Angle\tLongitude\tSign and Degree")
    for k, v in houses["angle"].items():
        just = "\t" if len(k) > 8 else "\t\t"
        print(str(k.title()) + just + str(round(v, 7)) + " \t" + convert_lat_to_sign(v))


def print_aspects(planets, midpoints):
    print("Aspects: Major")

    print()

    print("Planet A\tPlanet B\tAspect\t\tOrb")

    aspects = dict(
        zip(
            ["Conjunct", "Sextile", "Square", "Trine", "Opposite"],
            [0, 60, 90, 120, 180],
        )
    )
<<<<<<< HEAD
    ORB = [10, 10, 10, 10, 10]
=======
    ORB = [8, 8, 8, 8, 8]
>>>>>>> master

    for base_name, base_planet in planets.items():
        for planet, values in {**planets, **midpoints}.items():
            if planet != base_name:
                for aspect, degree in aspects.items():
                    justas = "\t" if len(aspect) >= 8 else "\t\t"
                    asp_orb = ORB[list(aspects.keys()).index(aspect)]
                    is_aspect, orb, distance, movement = calc_aspect(
                        base_planet, values, degree, asp_orb
                    )

                    if is_aspect:
                        just1 = "\t" if len(base_name) >= 8 else "\t\t"
                        just2 = "\t" if len(planet) >= 8 else "\t\t"
                        print(
                            f"{base_name}{just1}{planet}{just2}"
                            f"{aspect}{justas}{orb:.1f} {movement}"
                        )


def main():
    YEAR = 1994
    MONTH = 1
    DAY = 6
    HOUR = 19  # 11 am Pacific -> UTC time
    MINUTE = 47

    LAT = 37.386051
    LONG = -122.083855

    set_ephe_path()

    isvalid, jd, dt = calc_julian(YEAR, MONTH, DAY, HOUR, MINUTE)

    print(type(isvalid), type(jd), type(dt))
    planets = get_planets(jd, (swe.SUN, 20))
    houses = calc_houses(jd, LAT, LONG, hsys=b"P")
    midpoints = calc_midpoints(planets, [("Sun", "Moon")])

    for k, v in midpoints.items():
        midpoints[k] = calc_planet_pos(None, v, is_planet=False)

    ######## PRINTING AREA

    print_date(YEAR, MONTH, DAY, HOUR, MINUTE)

    print()
    print_planets(planets, houses)

    # print()
    # pprint.pprint(midpoints)

    # print()
    # print_houses(houses)

    # print()
    # print_angles(houses)

    # print()
    # print_aspects(planets, midpoints)


if __name__ == "__main__":
    print()
    main()
    print()
