from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from .config import settings
from .models import Appliance, Reading, Room

# Daily kWh targets for the simulated demonstration building. They are
# configuration targets, while every reported metric below is calculated from readings.
ROOM_BASELINES_KWH_PER_DAY = {
    "Bedroom": 8.5,
    "Living Room": 1.5,
    "Kitchen": 2.0,
    "Bathroom": 0.3,
}


def _window_start() -> datetime:
    return datetime(2026, 11, 24, 14) - timedelta(days=30)


def dashboard(db: Session) -> dict:
    start = _window_start()
    total = float(db.query(func.sum(Reading.energy_kwh)).filter(Reading.timestamp >= start).scalar() or 0)
    current = float(db.query(func.sum(Reading.power_watts)).filter(Reading.timestamp == datetime(2026, 11, 24, 13)).scalar() or 0)
    daily_rows = db.query(func.date(Reading.timestamp), func.sum(Reading.energy_kwh)).filter(Reading.timestamp >= start).group_by(func.date(Reading.timestamp)).order_by(func.date(Reading.timestamp)).all()
    room_rows = db.query(Room.name, func.sum(Reading.energy_kwh)).join(Appliance, Appliance.room_id == Room.id).join(Reading, Reading.appliance_id == Appliance.id).filter(Reading.timestamp >= start).group_by(Room.name).all()
    appliance_rows = db.query(Appliance.name, Appliance.category, Room.name, func.sum(Reading.energy_kwh)).join(Room, Room.id == Appliance.room_id).join(Reading, Reading.appliance_id == Appliance.id).filter(Reading.timestamp >= start).group_by(Appliance.id).order_by(func.sum(Reading.energy_kwh).desc()).limit(5).all()
    daily = [{"date": str(day)[5:], "kwh": round(float(kwh), 1)} for day, kwh in daily_rows]
    rooms = [{"name": name, "kwh": round(float(kwh), 1)} for name, kwh in room_rows]
    appliances = [{"name": name, "category": category, "room": room, "kwh": round(float(kwh), 1)} for name, category, room, kwh in appliance_rows]
    peak_room = max(rooms, key=lambda row: row["kwh"])["name"]
    score = max(35, min(96, round(100 - total / 18)))
    return {
        "simulated": True, "period_days": 31, "tariff_inr_per_kwh": settings.electricity_tariff,
        "carbon_factor_kg_per_kwh": settings.carbon_factor,
        "metrics": {"total_energy_kwh": round(total, 1), "current_power_watts": round(current), "monthly_bill_inr": round(total * settings.electricity_tariff), "carbon_kg": round(total * settings.carbon_factor, 1), "health_score": score},
        "daily_consumption": daily, "room_consumption": rooms, "top_appliances": appliances,
        "alerts": [
            {"severity": "high", "title": "Bedroom AC has extended overnight usage", "detail": "Simulated usage remained high for 7 consecutive hours."},
            {"severity": "medium", "title": f"{peak_room} is the highest-consuming room", "detail": "Review standby devices and cooling schedule."},
            {"severity": "low", "title": "Refrigerator load is stable", "detail": "Simulated compressor cycles are within normal range."},
        ],
    }


def rooms(db: Session) -> list[dict]:
    start = _window_start()
    rows = db.query(Room.name, Room.area_sqft, func.sum(Reading.energy_kwh)).join(Appliance, Appliance.room_id == Room.id).join(Reading, Reading.appliance_id == Appliance.id).filter(Reading.timestamp >= start).group_by(Room.id).all()
    return [{"name": name, "area_sqft": area, "energy_kwh": round(float(kwh), 1)} for name, area, kwh in rows]


def appliances(db: Session) -> list[dict]:
    start = _window_start()
    rows = db.query(Appliance.name, Appliance.category, Room.name, Appliance.rated_watts, func.sum(Reading.energy_kwh)).join(Room, Room.id == Appliance.room_id).join(Reading, Reading.appliance_id == Appliance.id).filter(Reading.timestamp >= start).group_by(Appliance.id).order_by(func.sum(Reading.energy_kwh).desc()).all()
    return [{"name": name, "category": category, "room": room, "rated_watts": watts, "energy_kwh": round(float(kwh), 1)} for name, category, room, watts, kwh in rows]


def _room_status(energy_kwh: float, baseline_kwh: float) -> tuple[str, float]:
    variance = ((energy_kwh - baseline_kwh) / baseline_kwh * 100) if baseline_kwh else 0
    if variance > 15:
        return "High usage", variance
    if variance > 0:
        return "Monitor", variance
    return "Efficient", variance


def room_analytics(db: Session) -> dict:
    """Building-level room comparison, dynamically aggregated from readings."""
    start = _window_start()
    period_days = 31
    rows = db.query(Room.name, Room.area_sqft, func.sum(Reading.energy_kwh)).join(
        Appliance, Appliance.room_id == Room.id
    ).join(Reading, Reading.appliance_id == Appliance.id).filter(
        Reading.timestamp >= start
    ).group_by(Room.id).all()
    building_total = sum(float(energy or 0) for _, _, energy in rows)
    room_rows = []
    for name, area_sqft, energy in rows:
        energy_kwh = float(energy or 0)
        baseline_kwh = ROOM_BASELINES_KWH_PER_DAY[name] * period_days
        status, variance = _room_status(energy_kwh, baseline_kwh)
        room_rows.append({
            "name": name,
            "area_sqft": area_sqft,
            "energy_kwh": round(energy_kwh, 1),
            "cost_inr": round(energy_kwh * settings.electricity_tariff),
            "percentage": round((energy_kwh / building_total * 100) if building_total else 0, 1),
            "baseline_kwh": round(baseline_kwh, 1),
            "variance_percent": round(variance, 1),
            "status": status,
            "waste_detected": variance > 15,
        })
    room_rows.sort(key=lambda room: room["energy_kwh"], reverse=True)
    highest = room_rows[0] if room_rows else None
    return {
        "simulated": True,
        "period_days": period_days,
        "tariff_inr_per_kwh": settings.electricity_tariff,
        "building_total_kwh": round(building_total, 1),
        "highest_consumption_room": highest,
        "rooms": room_rows,
    }


def room_detail(db: Session, room_name: str) -> dict | None:
    overview = room_analytics(db)
    room = next((entry for entry in overview["rooms"] if entry["name"].lower() == room_name.lower()), None)
    if room is None:
        return None
    start = _window_start()
    appliance_rows = db.query(
        Appliance.name, Appliance.category, Appliance.rated_watts, func.sum(Reading.energy_kwh)
    ).join(Room, Room.id == Appliance.room_id).join(Reading, Reading.appliance_id == Appliance.id).filter(
        Room.name == room["name"], Reading.timestamp >= start
    ).group_by(Appliance.id).order_by(func.sum(Reading.energy_kwh).desc()).all()
    connected_appliances = [{
        "name": name, "category": category, "rated_watts": watts, "energy_kwh": round(float(energy), 1),
        "cost_inr": round(float(energy) * settings.electricity_tariff),
    } for name, category, watts, energy in appliance_rows]
    history_rows = db.query(func.date(Reading.timestamp), func.sum(Reading.energy_kwh)).join(
        Appliance, Appliance.id == Reading.appliance_id
    ).join(Room, Room.id == Appliance.room_id).filter(
        Room.name == room["name"], Reading.timestamp >= start
    ).group_by(func.date(Reading.timestamp)).order_by(func.date(Reading.timestamp)).all()
    history = [{"date": str(day)[5:], "kwh": round(float(energy), 2)} for day, energy in history_rows]
    recommendations = []
    if room["waste_detected"]:
        recommendations.append(f"{room['name']} is {room['variance_percent']}% above its configured baseline; reduce avoidable runtime first.")
    top = connected_appliances[0] if connected_appliances else None
    if top and top["category"] == "Air conditioner":
        recommendations.append("Use a 24–26°C cooling setpoint and a timer to reduce overnight air-conditioner runtime.")
    if any(appliance["category"] == "Lights" for appliance in connected_appliances):
        recommendations.append("Switch off lights when the room is unoccupied; LED lighting keeps the same illumination with lower consumption.")
    if not recommendations:
        recommendations.append("Usage is within the configured baseline; keep monitoring appliance schedules to maintain this profile.")
    return {"simulated": True, "tariff_inr_per_kwh": settings.electricity_tariff, "room": room,
            "connected_appliances": connected_appliances, "consumption_history": history,
            "recommendations": recommendations}
