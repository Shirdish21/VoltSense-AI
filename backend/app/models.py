from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Room(Base):
    __tablename__ = "rooms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    area_sqft: Mapped[float] = mapped_column(Float)


class Appliance(Base):
    __tablename__ = "appliances"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(60))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    rated_watts: Mapped[float] = mapped_column(Float)


class Reading(Base):
    __tablename__ = "readings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    appliance_id: Mapped[int] = mapped_column(ForeignKey("appliances.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    power_watts: Mapped[float] = mapped_column(Float)
    energy_kwh: Mapped[float] = mapped_column(Float)
