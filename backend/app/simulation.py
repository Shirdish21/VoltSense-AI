"""Deterministic simulation: each reading represents one hour of energy use."""
from datetime import datetime, timedelta

import numpy as np
from sqlalchemy.orm import Session

from .models import Appliance, Reading, Room


ROOMS = [("Bedroom", 180), ("Living Room", 240), ("Kitchen", 140), ("Bathroom", 65)]
APPLIANCES = [
    ("Split Air Conditioner", "Air conditioner", "Bedroom", 1450, 0.58),
    ("Ceiling Fan", "Fan", "Bedroom", 72, 0.55),
    ("Bedroom Lights", "Lights", "Bedroom", 42, 0.38),
    ("Smart TV", "Other appliances", "Living Room", 110, 0.34),
    ("Living Room Fan", "Fan", "Living Room", 75, 0.62),
    ("Living Room Lights", "Lights", "Living Room", 54, 0.43),
    ("Refrigerator", "Refrigerator", "Kitchen", 180, 0.48),
    ("Washing Machine", "Washing machine", "Kitchen", 520, 0.16),
    ("Kitchen Lights", "Lights", "Kitchen", 36, 0.31),
    ("Water Heater", "Other appliances", "Bathroom", 1800, 0.08),
    ("Bathroom Lights", "Lights", "Bathroom", 22, 0.22),
]


def _activity(name: str, hour: int, base: float) -> float:
    if name == "Refrigerator":
        return base * (0.65 + (hour % 4) * 0.12)
    if "Air Conditioner" in name:
        return base * (1.0 if hour in range(21, 24) or hour in range(0, 7) else 0.08)
    if "Washing" in name:
        return base * (1.0 if hour in (10, 11, 12) else 0.02)
    if "Heater" in name:
        return base * (1.0 if hour in (7, 8) else 0.01)
    if "Lights" in name:
        return base * (1.0 if hour in range(18, 24) or hour in range(0, 6) else 0.18)
    if "Fan" in name:
        return base * (1.0 if hour in range(12, 24) else 0.42)
    return base * (1.0 if hour in range(18, 23) else 0.16)


def seed_database(db: Session) -> None:
    if db.query(Reading).first():
        return
    rooms = {name: Room(name=name, area_sqft=area) for name, area in ROOMS}
    db.add_all(rooms.values())
    db.flush()
    appliances = []
    for name, category, room_name, watts, activity in APPLIANCES:
        appliances.append(Appliance(name=name, category=category, room_id=rooms[room_name].id, rated_watts=watts))
    db.add_all(appliances)
    db.flush()

    rng = np.random.default_rng(20260101)
    end = datetime(2026, 11, 24, 14, 0, 0)
    records = []
    for days_ago in range(30, -1, -1):
        day = end - timedelta(days=days_ago)
        for hour in range(24):
            timestamp = day.replace(hour=hour)
            for appliance, spec in zip(appliances, APPLIANCES):
                load = _activity(spec[0], hour, spec[4])
                variation = float(rng.uniform(0.90, 1.10))
                watts = round(spec[3] * load * variation, 2)
                records.append(Reading(appliance_id=appliance.id, timestamp=timestamp, power_watts=watts, energy_kwh=round(watts / 1000, 4)))
    db.bulk_save_objects(records)
    db.commit()
