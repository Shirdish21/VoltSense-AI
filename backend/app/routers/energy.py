from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import appliances, room_analytics, room_detail, rooms

router = APIRouter(tags=["energy"])


@router.get("/api/rooms")
def get_rooms(db: Session = Depends(get_db)):
    return {"simulated": True, "rooms": rooms(db)}


@router.get("/api/appliances")
def get_appliances(db: Session = Depends(get_db)):
    return {"simulated": True, "appliances": appliances(db)}


@router.get("/api/room-analytics")
def get_room_analytics(db: Session = Depends(get_db)):
    return room_analytics(db)


@router.get("/api/room-analytics/{room_name}")
def get_room_detail(room_name: str, db: Session = Depends(get_db)):
    detail = room_detail(db, room_name)
    if detail is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return detail
