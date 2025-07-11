"""Presentation and formatting functions for astrological charts.

This module handles all the display logic, keeping it separate from chart calculations.
"""

import copy
from typing import Union

from rich.console import Console
from rich.table import Table

from starlight.objects import ASPECTS, get_ephemeris_object, format_long, format_long_sign


ASPECT_COLORS = {
    "Conjunct": "white",
    "Square": "red",
    "Opposition": "red",
    "Sextile": "green",
    "Trine": "green",
}


def create_table_sect(chart, plain: bool = True) -> str:
    """Determine day or night chart based on sun position relative to horizon."""
    sect = chart.get_sect()
    return f"{sect} Chart"


def create_table_dignities(chart, plain: bool) -> Union[Table, str]:
    """Create dignity scoring for each core planet."""
    
    output = "Planetary Dignities\n"
    output += "-" * 40 + "\n"

    dignity_scores = chart.get_planetary_dignities()
    
    for planet_name, score in dignity_scores.items():
        output += f"{planet_name:<12} | {score:>3}\n"
    
    return output


def create_table_planets(chart, plain: bool, fmt: str = "plain") -> Union[Table, str]:
    """Create a table of all planet placements for display."""
    
    if fmt == "word":
        output = ""
        output += "Planet Placements:\n"
        for p in chart.planets:
            house = chart.get_planet_house(p)
            display_name = get_ephemeris_object(p.swe)["alias"]
            retro = "Retrograde" if p.is_retro is True else ""
            output += f"{display_name} is in {p.sign} at {p.sign_deg_str}"
            if len(retro) > 0:
                output += f" ({retro})"
            if chart.is_time_known:
                output += f" in House {house}"
            output += ".\n"
        return output

    if plain is True:
        output = "Planet Placements\n"
        output += "-" * 70 + "\n"
        for p in chart.planets:
            house = chart.get_planet_house(p)
            display_name = get_ephemeris_object(p.swe)["alias"]
            retro = "Retrograde" if p.is_retro is True else ""
            output += f"{display_name:>13} | {p.sign:<12} | {p.sign_deg_str:<10} | {retro:10} | House {house}\n"
        return output

    else:
        table_planets = Table(title="Planet Placements")

        for column in ["Planet", "ID", "Sign", "Longitude", "Speed", "Sign Degrees"]:
            table_planets.add_column(column)

        for p in chart.planets:
            row = [
                p.name,
                str(p.swe),
                p.sign,
                f"{round(p.long, 2)}°",
                f"{round(p.speed_long, 2)}",
                p.sign_deg_str,
            ]
            table_planets.add_row(*row)

        return table_planets


def create_table_houses(chart, plain: bool, fmt: str = "plain") -> Union[Table, str]:
    """Create a table of house cusps."""
    if fmt == "word":
        output = ""
        output += "House Cusps\n"
        for i, c in enumerate(chart.cusps):
            output += f"House {i+1} is ruled by {format_long_sign(c)}.\n"
        return output
    if plain is True:
        output = "House Cusps\n"
        output += "-" * 30 + "\n"
        for i, c in enumerate(chart.cusps):
            output += f"{i+1:>3} | {format_long_sign(c):<12} | {format_long(c):<10}\n"
        return output

    else:
        table_cusps = Table(title="House Cusps")
        for col in ["House", "Cusp Sign", "Cusp Degrees"]:
            table_cusps.add_column(col)

        for i, c in enumerate(chart.cusps):
            table_cusps.add_row(str(i + 1), format_long_sign(c), format_long(c))

        return table_cusps


def create_table_angles(chart, plain: bool, fmt: str = "plain") -> Union[Table, str]:
    """Create a table of chart angles."""
    if fmt == "word":
        output = ""
        output += "Chart Angles:\n"
        for angle in chart.angles:
            display_name = get_ephemeris_object(angle.name)["alias"]
            if angle.name in ["ASC", "MC", "VERTEX"]:
                output += f"{display_name} is at {format_long(angle.long)} {format_long_sign(angle.long)}.\n"
            if angle.name in ["ASC", "MC"]:
                new_long = (angle.long + 180) % 360
                new_name_map = {"ASC": "DSC", "MC": "IC"}
                new_name = new_name_map[angle.name]
                new_dname = get_ephemeris_object(new_name)["alias"]
                output += f"{new_dname} is at {format_long(new_long)} {format_long_sign(new_long)}.\n"
        return output

    if plain is True:
        output = "Chart Angles\n"
        output += "-" * 30 + "\n"
        for angle in chart.angles:
            display_name = get_ephemeris_object(angle.name)["alias"]
            if angle.name in ["ASC", "MC", "VERTEX"]:
                output += f"{display_name:<6} | {format_long_sign(angle.long):<12} | {format_long(angle.long):<10}\n"
                if angle.name in ["ASC", "MC"]:
                    new_long = (angle.long + 180) % 360
                    new_name = "DSC" if angle.name == "ASC" else "IC"
                    new_dname = get_ephemeris_object(new_name)["alias"]
                    output += f"{new_dname:<6} | {format_long_sign(new_long):<12} | {format_long(new_long):<10}\n"
        return output
    else:
        table_angles = Table(title="Chart Angles")
        for col in ["Name", "ID", "Sign", "Degrees"]:
            table_angles.add_column(col)

        for angle in chart.angles:
            table_angles.add_row(
                angle.name,
                str(angle.swe),
                format_long_sign(angle.long),
                format_long(angle.long),
            )
            if angle.name in ["ASC", "MC"]:
                new_long = (angle.long + 180) % 360
                new_name = "DSC" if angle.name == "ASC" else "IC"
                table_angles.add_row(
                    new_name,
                    str(angle.swe),
                    format_long_sign(new_long),
                    format_long(new_long),
                )

        return table_angles


def create_table_aspects(chart, plain: bool, fmt: str = "plain") -> Union[Table, str]:
    """Create a table of all planet aspects."""
    if plain is True:
        output = "Planet Aspects:\n"
        if fmt == "plain":
            output += "-" * 60 + "\n"
        pairs = []
        for p in chart.planets:
            for other_obj in [*chart.planets, *chart.angles]:
                if (
                    (other_obj.name != p.name)
                    and (
                        other_obj.swe in list(range(12))
                        or other_obj.name in ["ASC", "MC", "DSC", "IC"]
                    )
                    and ((p, other_obj) not in pairs)
                ):
                    for a, v in ASPECTS.items():
                        aspect = p.aspect(other_obj, v["degree"], v["orb"])
                        if aspect[0]:
                            name1 = get_ephemeris_object(p.swe)["alias"]
                            if other_obj.swe is not None:
                                name2 = get_ephemeris_object(other_obj.swe)["alias"]
                            else:
                                name2 = get_ephemeris_object(other_obj.name)["alias"]
                            color = ASPECT_COLORS.get(a, "white")
                            if fmt == "word":
                                output += f"{name1} is {a} {name2} ({round(aspect[1])}° orb {aspect[3]}).\n"
                            else:
                                output += f"{name1:>13} | {name2:<13} | [{color}]{a:<10}[/{color}] | {round(aspect[1]):>2}° | {aspect[3]}\n"
                            pairs.append((other_obj, p))
            output += "\n"

        return output
    else:
        table_aspects = Table(title="Planet Aspects")
        for col in ["Planet A", "Planet B", "Aspect", "Orb", "Movement"]:
            table_aspects.add_column(col)

        for p in chart.planets:
            if p.swe in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                for other_obj in [*chart.planets, *chart.angles]:
                    if (other_obj.name != p.name) and other_obj.swe in list(range(13)):
                        for a, v in ASPECTS.items():
                            aspect = p.aspect(other_obj, v["degree"], v["orb"])
                            if aspect[0]:
                                row_list = [
                                    p.name,
                                    other_obj.name,
                                    a,
                                    f"{round(aspect[1])}°",
                                    aspect[3] if aspect[3] is not None else "-",
                                ]
                                table_aspects.add_row(*row_list)

        return table_aspects


def create_table_midpoints(chart, plain: bool) -> str:
    """Create a table of chart midpoints and their aspects."""
    output = "Chart Midpoints\n"
    output += "-" * 42 + "\n"
    for mp in chart.midpoints:
        name = f"{mp.obj1.name}-{mp.obj2.name}"
        output += f"{name:14} | {format_long_sign(mp.long):<12} | {format_long(mp.long):<10}\n"

    output += "\nMidpoint Aspects\n"
    output += "-" * 60 + "\n"
    for mp in chart.midpoints:
        name = f"{mp.obj1.name}-{mp.obj2.name}"
        for p in chart.planets:
            # use closer midpoint
            mp_2 = copy.deepcopy(mp)
            mp_2.long = (mp.long + 180) % 360
            if abs(p.long - mp.long) < abs(p.long - mp_2.long):
                mp_close = mp
            else:
                mp_close = mp_2
            for a, v in ASPECTS.items():
                aspect = mp_close.aspect(p, v["degree"], v["orb"])
                if aspect[0]:
                    color = ASPECT_COLORS.get(a, "white")
                    pname = get_ephemeris_object(p.swe)["alias"]
                    output += f"{name:>14} | {pname:<12} | [{color}]{a:<10}[/{color}] | {round(aspect[1]):>2}° | {aspect[3]}\n"
        output += "\n"
    return output


def print_chart_summary(chart, console: Console, plain: bool = False, fmt: str = "plain") -> None:
    """Print a complete chart summary with all tables."""
    chart.print_date()
    console.print()
    console.print(create_table_planets(chart, plain=plain, fmt=fmt))
    console.print(create_table_houses(chart, plain=plain, fmt=fmt))
    console.print(create_table_angles(chart, plain=plain, fmt=fmt))
    console.print(create_table_aspects(chart, plain=plain, fmt=fmt))