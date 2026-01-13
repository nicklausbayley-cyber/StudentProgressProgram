from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app import schemas, crud
from app.deps import get_current_user, require_roles
from app.models import Role

router = APIRouter(prefix="/students", tags=["students"], dependencies=[Depends(require_roles(Role.admin, Role.counselor))])

@router.post("", response_model=schemas.StudentOut, dependencies=[Depends(require_roles(Role.admin, Role.counselor))])
async def create_student(payload: schemas.StudentCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_student(db, payload)

@router.get("", response_model=list[schemas.StudentOut], dependencies=[Depends(require_roles(Role.admin, Role.counselor))])
async def list_students(db: AsyncSession = Depends(get_db), limit: int = 100, offset: int = 0):
    return await crud.list_students(db, limit=limit, offset=offset)

@router.get("/me", response_model=schemas.StudentWithLatest)
async def my_student_record(user = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role != Role.student or user.student_id is None:
        raise HTTPException(status_code=403, detail="Not a student account")
    student = await crud.get_student(db, user.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    latest = await crud.latest_metric_for_student(db, student.id)
    return schemas.StudentWithLatest(student=student, latest_metric=latest)

@router.get("/{student_id}", response_model=schemas.StudentWithLatest, dependencies=[Depends(require_roles(Role.admin, Role.counselor))])
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    student = await crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    latest = await crud.latest_metric_for_student(db, student_id)
    return schemas.StudentWithLatest(student=student, latest_metric=latest)
