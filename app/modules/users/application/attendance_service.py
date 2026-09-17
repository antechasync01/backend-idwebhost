from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from app.modules.users.infrastructure.models import Attendance, User

class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    def clock_in(self, user_id: UUID) -> Attendance:
        now = datetime.now(timezone.utc)
        
        # Check if already clocked in today
        existing = self.db.query(Attendance).filter(
            Attendance.user_id == user_id,
            Attendance.date == now.date()
        ).first()

        if existing:
            raise ValueError("Opening toko hanya perlu dilakukan sekali saja dalam satu hari.")

        now = datetime.now(timezone.utc)
        attendance = Attendance(
            user_id=user_id,
            clock_in_time=now,
            date=now.date()
        )
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance

    def clock_out(self, user_id: UUID) -> Attendance:
        existing = self.db.query(Attendance).filter(
            Attendance.user_id == user_id,
            Attendance.clock_out_time.is_(None)
        ).first()

        if not existing:
            raise ValueError("You are not currently clocked in.")

        now = datetime.now(timezone.utc)
        existing.clock_out_time = now
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def is_clocked_in(self, user_id: UUID) -> bool:
        now = datetime.now(timezone.utc)
        existing = self.db.query(Attendance).filter(
            Attendance.user_id == user_id,
            Attendance.date == now.date()
        ).first()
        return existing is not None

    def get_status(self, user_id: UUID) -> dict:
        now = datetime.now(timezone.utc)
        existing = self.db.query(Attendance).filter(
            Attendance.user_id == user_id,
            Attendance.date == now.date()
        ).first()
        
        if existing:
            return {
                "is_clocked_in": True,
                "clock_in_time": existing.clock_in_time.isoformat()
            }
        else:
            return {
                "is_clocked_in": False,
                "last_clock_out": None
            }
