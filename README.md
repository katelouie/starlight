# Usage Notes

Check out `usage.py` to see the outputs and breakdown of a given chart. 
They can be formatted either plaintext or using `rich` tables.

The `data` folder should exist within `src/starlight` as a directory at the same level as the main function files (`chart.py`, etc.). It holds a large number of files you can download from the Swiss Ephemeris resource FTP.

# Development Plan

steps to complete:

- [x] can input a date + time + location and get back all of the planetary positions (raw)
- [x] can output the planets position (longitude) in the signs
- [x] can calculate the asc
- [x] can apply the house system (whole sign) and generate MC / Dsc / IC
- [x] can apply the placidus house system too

## input
- [x] Allow inputting city name and state/country to get coordinates
- [x] Allow inputting local time and converts it to UTC

## chart analysis

- [x] generate calculated midpoints
- [ ] Note when a body is retrograde
- [x] generate aspect calculations for main planets (lights + personal + impersonal + generational)
  - [x] major
  - [x] minor
  - [x] orb
  - [x] apply/seperate
- [x] generate aspects w/ midpoints and any other arbitrary points / objects / angles

- [x] allow setting orb values
- [x] allow selecting type of aspects calculated
- [x] allow selecting objects to calculate aspects for

## extra planet info

- [x] speed
- [x] latitude
- [x] declination
- [x] retrograde / direct markers
- [ ] Moon - phase of the moon

## output

- [ ] draw basic chart with planets / signs / houses / angles
- [ ] allow multiple house systems in single chart (?)
- [x] output table for planet positions
  - [x] add cusps
  - [x] add angles
  - [x] add houses to position chart
- [x] output table for aspects (row-based)
  - [ ] output table with selected ordering: by orb, by other object, by aspect type
- [ ] output table for aspects (triangle)
- [ ] draw chart with aspects

## chart analysis output

- [ ] element and modality balance
- [ ] calculate dispositor flows
- [ ] energy pairings of "astrological alphabet"
- [ ] most common aspect
- [ ] any larger aspect configurations (ie stellium, grand trine, t square, etc.)

## Development Notes to Self

[returns of `calc_` functions](https://astrorigin.com/pyswisseph/sphinx/programmers_manual/planetary_positions/position_and_speed.html)

https://astrorigin.com/pyswisseph/
https://astrorigin.com/pyswisseph/sphinx/index.html
https://astrorigin.com/pyswisseph/pydoc/index.html
