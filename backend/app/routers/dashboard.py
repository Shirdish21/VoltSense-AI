from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import dashboard

router = APIRouter(tags=["dashboard"])


@router.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    return dashboard(db)
