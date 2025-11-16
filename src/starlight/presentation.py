"""Presentation and formatting functions for astrological charts.

This module handles all the display logic, keeping it separate from chart calculations.
"""

import copy
from typing import Union

from rich.console import Console
from rich.table import Table

from starlight.core.registry import get_aspect_by_alias, get_aspect_info
from starlight.objects import (
    ASPECTS,
    format_long,
    format_long_sign,
    get_ephemeris_object,
)


def get_aspect_color_for_terminal(aspect_name: str) -> str:
    """
    Get terminal color name for an aspect based on registry color.

    Maps hex colors from the aspect registry to terminal color names.

    Args:
        aspect_name: Aspect name (e.g., "Conjunction", "Conjunct")

    Returns:
        Terminal color name (e.g., "red", "green", "white")
    """
    # Try exact name first
    aspect_info = get_aspect_info(aspect_name)
    if not aspect_info:
        # Try as alias (e.g., "Conjunct" → "Conjunction")
        aspect_info = get_aspect_by_alias(aspect_name)

    if not aspect_info:
        return "white"  # Default fallback

    # Map hex colors to terminal color names
    color_map = {
        "#E74C3C": "red",      # Opposition, Square (challenging)
        "#F39C12": "red",      # Square (also challenging)
        "#3498DB": "green",    # Trine (harmonious)
        "#27AE60": "green",    # Sextile (harmonious)
        "#34495E": "white",    # Conjunction (neutral)
        "#9B59B6": "magenta",  # Quincunx
        "#95A5A6": "white",    # Semisextile
        "#E67E22": "yellow",   # Semisquare
        "#D68910": "yellow",   # Sesquisquare
    }

    return color_map.get(aspect_info.color, "white")


def create_table_sect(chart, plain: bool = True) -> str:
    """Determine day or night chart based on sun position relative to horizon."""
    sect = chart.get_sect()
    return f"{sect} Chart"


def create_table_dignities(chart, plain: bool, traditional: bool = True) -> Union[Table, str]:
    """Create dignity scoring for each core planet."""

    dignity_type = "Traditional" if traditional else "Modern"
    
    if plain is True:
        output = f"Planetary Dignities ({dignity_type})\n"
        output += "-" * 70 + "\n"
        output += f"Chart Sect: {chart.get_sect()}\n"
        output += "-" * 70 + "\n"
        output += f"{'Planet':<10} | {'Sign':<12} | {'Deg':<6} | {'Dignities':<25} | Score\n"
        output += "-" * 70 + "\n"

        dignity_data = chart.get_planetary_dignities(traditional=traditional)

        # Sort planets by total score (highest first)
        sorted_planets = sorted(dignity_data.items(), key=lambda x: x[1]['total_score'], reverse=True)

        for planet_name, data in sorted_planets:
            dignities_str = ", ".join(data['dignities']) if data['dignities'] else "None"
            output += f"{planet_name:<10} | {data['sign']:<12} | {data['degree']:>5.1f}° | {dignities_str:<25} | {data['total_score']:>3}\n"
        
        # Also show bounds and decan rulers
        output += "\nBounds & Decan Rulers\n"
        output += "-" * 50 + "\n"
        for planet_name, data in dignity_data.items():
            output += f"{planet_name:<10} | Bound: {data['bound_ruler']:<10} | Decan: {data['decan_ruler']}\n"

        return output
    
    else:
        # Rich table version
        dignity_data = chart.get_planetary_dignities(traditional=traditional)
        
        # Main dignities table
        table_dignities = Table(title=f"Planetary Dignities ({dignity_type})")
        table_dignities.caption = f"Chart Sect: {chart.get_sect()}"
        
        table_dignities.add_column("Planet", style="bold")
        table_dignities.add_column("Sign") 
        table_dignities.add_column("Degree", justify="right")
        table_dignities.add_column("Dignities")
        table_dignities.add_column("Score", justify="right", style="bold")

        # Sort planets by total score (highest first)
        sorted_planets = sorted(dignity_data.items(), key=lambda x: x[1]['total_score'], reverse=True)

        for planet_name, data in sorted_planets:
            dignities_str = ", ".join(data['dignities']) if data['dignities'] else "None"
            score_color = "green" if data['total_score'] > 0 else "red" if data['total_score'] < 0 else "white"
            
            table_dignities.add_row(
                planet_name,
                data['sign'],
                f"{data['degree']:.1f}°",
                dignities_str,
                f"[{score_color}]{data['total_score']}[/{score_color}]"
            )
        
        # Bounds & Decan rulers table
        table_bounds = Table(title="Bounds & Decan Rulers")
        table_bounds.add_column("Planet", style="bold")
        table_bounds.add_column("Bound Ruler")
        table_bounds.add_column("Decan Ruler")
        
        for planet_name, data in dignity_data.items():
            table_bounds.add_row(
                planet_name,
                data['bound_ruler'],
                data['decan_ruler']
            )
        
        # Return both tables as a group
        from rich.console import Group
        return Group(table_dignities, "", table_bounds)


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

        for column in ["Planet", "Sign", "Sign Degrees", "Retrograde", "House"]:
            table_planets.add_column(column)

        for p in chart.planets:
            house = chart.get_planet_house(p)
            display_name = get_ephemeris_object(p.swe)["alias"]
            retro = "Rx" if p.is_retro is True else ""
            
            row = [
                display_name,
                p.sign,
                p.sign_deg_str,
                retro,
                f"House {house}",
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
                            color = get_aspect_color_for_terminal(a)
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


def print_chart_summary(
    chart, console: Console, plain: bool = False, fmt: str = "plain"
) -> None:
    """Print a complete chart summary with all tables."""
    chart.print_date()
    console.print()
    console.print(create_table_planets(chart, plain=plain, fmt=fmt))
    console.print(create_table_houses(chart, plain=plain, fmt=fmt))
    console.print(create_table_angles(chart, plain=plain, fmt=fmt))
    console.print(create_table_aspects(chart, plain=plain, fmt=fmt))
