"""
The Native class represents the core data for a single person or event.

Its job is to handle messy inputs (strings, dicts, naive datetimes, etc.) and process
them into the clean, immutable ChartDateTime and ChartLocation objects
that the rest of the system requires.
"""

import datetime as dt
from typing import Any

import pytz
import swisseph as swe
from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from starlight.core.models import ChartDateTime, ChartLocation
from starlight.utils.cache import cached

# Define the messy input types we'll accept
DateTimeInput = dt.datetime | ChartDateTime | dict[str, Any]
LocationInput = str | ChartLocation | tuple[float, float] | dict[str, float | str]


class Native:
    """
    Represents the "native" data (time and place) for a chart.
    This class handles all the input parsing and data cleaning.
    """

    datetime: ChartDateTime
    location: ChartLocation

    def __init__(
        self, datetime_input: DateTimeInput, location_input: LocationInput
    ) -> None:
        """Creates a new Native object by parsing flexible inputs.

        Args:
            datetime_input: Can be a timezone-aware datetime, a dict, or
                a pre-made ChartDateTime object
            location_input: Can be a string to geocode, a (lat, lon) tuple,
                a dict, or a pre-made ChartLocation object
        """
        self.location = self._process_location(location_input)
        self.datetime = self._process_datetime(datetime_input, self.location.timezone)

    def _process_location(self, loc_in: LocationInput) -> ChartLocation:
        """Internal helper to parse any location input."""

        # 1. Already have a ChartLocation? We're done
        if isinstance(loc_in, ChartLocation):
            return loc_in

        # 2. A string? Geocode it.
        if isinstance(loc_in, str):
            location_data = _cached_geocode(loc_in)
            if not location_data:
                raise ValueError(f"Could not geocode location: {loc_in}")
            return ChartLocation(
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                name=location_data["address"],
                timezone=location_data["timezone"],
            )

        # 3. A tuple? Assume (lat, lon)
        if isinstance(loc_in, tuple) and len(loc_in) == 2:
            lat, lon = loc_in

            # Find the timezone for this lat/lon
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"

            return ChartLocation(
                latitude=float(lat),
                longitude=float(lon),
                name=f"{lat}, {lon}",
                timezone=timezone_str,
            )

        # 4. A dict? Assume {lat, lon, ...}
        if isinstance(loc_in, dict):
            if "latitude" not in loc_in or "longitude" not in loc_in:
                raise ValueError(
                    "Location dict must contain 'latitude' and 'longitude'"
                )
            lat = float(loc_in["latitude"])
            lon = float(loc_in["longitude"])

            # Find timezone if not provided
            timezone_str = loc_in.get("timezone")
            if not timezone_str:
                tf = TimezoneFinder()
                timezone_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"

            return ChartLocation(
                latitude=lat,
                longitude=lon,
                name=str(loc_in.get("name", f"{lat}, {lon}")),
                timezone=str(timezone_str),
            )

        raise TypeError(f"Unsupported location input type: {type(loc_in)}")

    def _process_datetime(
        self, time_input: DateTimeInput, loc_timezone: str
    ) -> ChartDateTime:
        """
        Parses any time input into a ChartDateTime object.

        Args:
            time_input: A dt.datetime, dict, or ChartDateTime.
            location_timezone: The IANA timezone string (e.g., "America/New_York")
                               found during location parsing.
        """
        # 1. Already a ChartDateTime? We're done.
        if isinstance(time_input, ChartDateTime):
            return time_input

        utc_dt: dt.datetime | None = None
        local_dt: dt.datetime | None = None

        # 2. Datetime Object Input
        if isinstance(time_input, dt.datetime):
            local_dt = time_input  # Store for the final object
            if time_input.tzinfo is None:
                # Naive datetime. Localize it using the location's timezone.
                if not loc_timezone:
                    raise ValueError(
                        "Datetime is naive (no timezone) and location has no timezone. "
                        "Cannot determine time."
                    )
                try:
                    loc_tz = pytz.timezone(loc_timezone)
                    aware_dt = loc_tz.localize(time_input)
                    utc_dt = aware_dt.astimezone(dt.UTC)
                except pytz.UnknownTimeZoneError:
                    raise ValueError(
                        f"Invalid location timezone: {loc_timezone}"
                    ) from pytz.UnknownTimeZoneError
            else:
                # Aware datetime. Just convert to UTC.
                utc_dt = time_input.astimezone(dt.UTC)

        # 3. Dictionary Input
        elif isinstance(time_input, dict):
            try:
                naive_dt = dt.datetime(
                    year=int(time_input["year"]),
                    month=int(time_input["month"]),
                    day=int(time_input["day"]),
                    hour=int(time_input.get("hour", 0)),
                    minute=int(time_input.get("minute", 0)),
                    second=int(time_input.get("second", 0)),
                )
                local_dt = naive_dt  # Store this as the local time

                # Now, use the location's timezone to make it aware
                if not loc_timezone:
                    raise ValueError(
                        "Time was input as a dict (naive) and location has no timezone. "
                        "Cannot determine time."
                    )
                try:
                    loc_tz = pytz.timezone(loc_timezone)
                    aware_dt = loc_tz.localize(naive_dt)
                    utc_dt = aware_dt.astimezone(dt.UTC)
                    local_dt = aware_dt  # Store the *aware* local time
                except pytz.UnknownTimeZoneError:
                    raise ValueError(
                        f"Invalid location timezone: {loc_timezone}"
                    ) from pytz.UnknownTimeZoneError

            except KeyError as e:
                raise KeyError(f"Missing required time key in dict: {e}") from KeyError
            except Exception as e:
                raise ValueError(f"Error parsing time dict: {e}") from Exception

        else:
            raise TypeError(f"Invalid datetime_input type: {type(time_input)}")

        # --- Final Conversion ---
        if utc_dt:
            # Calculate Julian day from the (now guaranteed) UTC datetime
            # We must use the UTC time for swe.julday to get ET
            hour_decimal = (
                (utc_dt.minute / 60.0)
                + (utc_dt.second / 3600.0)
                + (utc_dt.microsecond / 3600000000.0)
            )
            julian_day_et = swe.julday(
                utc_dt.year,
                utc_dt.month,
                utc_dt.day,
                utc_dt.hour + hour_decimal,
            )

            # Get Delta T and convert to Julian Day UT (Universal Time)
            # This is the correct Julian Day for calculations.
            delta_t = swe.deltat(julian_day_et)
            julian_day_ut = julian_day_et - delta_t

            return ChartDateTime(
                utc_datetime=utc_dt, julian_day=julian_day_ut, local_datetime=local_dt
            )

        raise ValueError("Could not parse datetime input.")


# --- Geocoding Helper ---
@cached(cache_type="geocoding", max_age_seconds=604800)
def _cached_geocode(location_name: str) -> dict:
    """Cached geocoding."""
    try:
        geolocator = Nominatim(user_agent="starlight_astrology_package")
        location = geolocator.geocode(location_name)
        if location:
            lat, lon = location.latitude, location.longitude

            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lng=lon, lat=lat)
            return {
                "latitude": lat,
                "longitude": lon,
                "address": str(location),
                "timezone": timezone_str,
            }
        return {}
    except GeocoderUnavailable:
        print("Warning: Geocoding service is unavailable.")
        return {}
    except Exception as e:
        print(f"Warning: Geocoding error: {e}")
        return {}
