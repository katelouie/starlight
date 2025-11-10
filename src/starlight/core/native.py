"""
The Native class represents the core data for a single person or event.

Its job is to handle messy inputs (strings, dicts, etc.) and process
them into the clean, immutable ChartDateTime and ChartLocation objects
that the rest of the system requires.
"""

import datetime as dt
from typing import Any

import pytz
import swisseph as swe
from geopy.geocoders import Nominatim

from starlight.cache import cached
from starlight.core.models import ChartDateTime, ChartLocation

# Define the messy input types we'll accept
DateTimeInput = dt.datetime | ChartDateTime | dict[str, Any]
LocationInput = str | ChartLocation | tuple[float, float] | dict[str, float]


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
        self.datetime = self._process_datetime(datetime_input)

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
            )

        # 3. A tuple? Assume (lat, lon)
        if isinstance(loc_in, tuple) and len(loc_in) == 2:
            return ChartLocation(latitude=loc_in[0], longitude=loc_in[1])

        # 4. A dict? Assume {lat, lon, ...}
        if isinstance(loc_in, dict):
            if "latitude" not in loc_in or "longitude" not in loc_in:
                raise ValueError(
                    "Location dict must contain 'latitude' and 'longitude'"
                )
            return ChartLocation(
                latitude=loc_in["latitude"], longitude=loc_in["longitude"]
            )

        raise TypeError(f"Unsupported location input type: {type(loc_in)}")

    def _process_datetime(self, dt_in: DateTimeInput) -> ChartDateTime:
        """Internal helepr to parse any datetime input."""
        # 1. Already a ChartDateTime? We're done.
        if isinstance(dt_in, ChartDateTime):
            return dt_in

        datetime_to_process: dt.datetime

        # 2. A standard datetime object
        if isinstance(dt_in, dt.datetime):
            if dt_in.tzinfo is None:
                raise ValueError("datetime input must be timezone-aware.")
            datetime_to_process = dt_in

        # 3. A dict of components
        elif isinstance(dt_in, dict):
            # Requires 'year', 'month', 'day' and a 'timezone' string.
            # 'hour', 'minute', 'second' are optional.
            try:
                tz_str = dt_in["timezone"]
                tz = pytz.timezone(tz_str)
                datetime_to_process = tz.localize(
                    dt.datetime(
                        year=dt_in["year"],
                        month=dt_in["month"],
                        day=dt_in["day"],
                        hour=dt_in.get("hour", 0),
                        minute=dt_in.get("minute", 0),
                        second=dt_in.get("second", 0),
                    )
                )
            except Exception as e:
                raise ValueError(f"Could not parse datetime dict: {e}") from Exception

        else:
            raise TypeError(f"Unsupported datetime input type: {type(dt_in)}")

        # Now we process the clean datetime
        utc_dt = datetime_to_process.astimezone(dt.UTC)
        hour_decimal = utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        julian_day = swe.date_conversion(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + hour_decimal,
        )[1]

        return ChartDateTime(
            utc_datetime=utc_dt,
            julian_day=julian_day,
            local_datetime=datetime_to_process,
        )


# --- Geocoding Helper ---
@cached(cache_type="geocoding", max_age_seconds=604800)
def _cached_geocode(location_name: str) -> dict:
    """Cached geocoding."""
    try:
        geolocator = Nominatim(user_agent="starlight_astrology_package")
        location = geolocator.geocode(location_name)
        if location:
            return {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": str(location),
            }
        return {}
    except Exception as e:
        print(f"Geocoding error: {e}")
        return {}
