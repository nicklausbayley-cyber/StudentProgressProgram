from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app import schemas, crud
from app.deps import require_roles
from app.models import Role

router = APIRouter(prefix="/metrics", tags=["metrics"], dependencies=[Depends(require_roles(Role.admin, Role.counselor))])

@router.post("/students/{student_id}", response_model=schemas.MetricOut, dependencies=[Depends(require_roles(Role.admin, Role.counselor))])
async def add_metric(student_id: int, payload: schemas.MetricIn, db: AsyncSession = Depends(get_db)):
    student = await crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return await crud.add_metric(db, student_id, payload)
