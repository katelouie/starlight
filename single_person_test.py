#!/usr/bin/env python3
"""Test single person to debug geocoding"""

import sys
sys.path.insert(0, "src")

from datetime import datetime
import pytz
from starlight.chart import Chart

# Test with Albert Einstein (known to fail)
person_data = {
    "name": "Albert Einstein",
    "date": "1879-03-14",
    "time": "11:30",
    "location": "Ulm, Germany",
    "latitude": 48.3984,
    "longitude": 9.9916,
    "timezone": "Europe/Berlin",
}

print(f"Testing chart creation for {person_data['name']}...")
print(f"Location: {person_data['location']}")
print(f"Coordinates: ({person_data['latitude']}, {person_data['longitude']})")

try:
    # Parse birth data and convert to UTC
    birth_date = datetime.strptime(person_data["date"], "%Y-%m-%d").date()
    birth_time = datetime.strptime(person_data["time"], "%H:%M").time()
    birth_datetime = datetime.combine(birth_date, birth_time)

    # Make timezone-aware and convert to UTC
    local_tz = pytz.timezone(person_data["timezone"])
    birth_datetime_local = local_tz.localize(birth_datetime)
    birth_datetime_utc = birth_datetime_local.astimezone(pytz.UTC)

    print(f"UTC datetime: {birth_datetime_utc}")
    print("Creating Chart...")
    
    # Create chart - Chart expects UTC datetime and location tuple
    chart = Chart(
        datetime_utc=birth_datetime_utc,
        houses="Placidus",
        loc=(person_data["latitude"], person_data["longitude"]),
        loc_name=person_data["location"],
    )
    
    print("✓ Chart created successfully!")
    print(f"Chart location: {chart.loc}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()