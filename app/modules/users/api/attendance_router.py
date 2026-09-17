from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.responses import create_response
from app.modules.users.application.attendance_service import AttendanceService
from app.modules.users.infrastructure.models import User

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/clock-in", status_code=status.HTTP_200_OK)
def clock_in(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AttendanceService(db)
    try:
        attendance = service.clock_in(current_user.id)
        return create_response(
            message="Clock in successful",
            data={"clock_in_time": attendance.clock_in_time.isoformat()}
        )
    except ValueError as e:
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e)
        )

@router.post("/clock-out", status_code=status.HTTP_200_OK)
def clock_out(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AttendanceService(db)
    try:
        attendance = service.clock_out(current_user.id)
        return create_response(
            message="Clock out successful",
            data={"clock_out_time": attendance.clock_out_time.isoformat() if attendance.clock_out_time else None}
        )
    except ValueError as e:
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e)
        )

@router.get("/status", status_code=status.HTTP_200_OK)
def get_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = AttendanceService(db)
    status_data = service.get_status(current_user.id)
    return create_response(
        data=status_data
    )
