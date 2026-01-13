import csv
import io
from datetime import date
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_db
from app.deps import require_roles
from app.models import Role, Student, GrowthStatus
from app import crud, schemas

router = APIRouter(prefix="/imports", tags=["imports"], dependencies=[Depends(require_roles(Role.admin, Role.counselor))])

@router.post("/students_csv", dependencies=[Depends(require_roles(Role.admin, Role.counselor))])
async def import_students_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # CSV columns: local_student_id,first_name,last_name,grade_level,diploma_path
    raw = await file.read()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    created = 0
    for row in reader:
        payload = schemas.StudentCreate(
            local_student_id=row["local_student_id"].strip(),
            first_name=row["first_name"].strip(),
            last_name=row["last_name"].strip(),
            grade_level=int(row["grade_level"]),
            diploma_path=(row.get("diploma_path") or "").strip() or None,
        )
        # upsert by local_student_id
        res = await db.execute(select(Student).where(Student.local_student_id == payload.local_student_id))
        existing = res.scalar_one_or_none()
        if existing:
            existing.first_name = payload.first_name
            existing.last_name = payload.last_name
            existing.grade_level = payload.grade_level
            existing.diploma_path = payload.diploma_path
        else:
            db.add(Student(**payload.model_dump()))
            created += 1
    await db.commit()
    return {"created": created}

@router.post("/metrics_csv", dependencies=[Depends(require_roles(Role.admin, Role.counselor))])
async def import_metrics_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    # CSV columns: local_student_id,as_of_date,attendance_percentage,growth_status,credits_earned,expected_credits_for_grade
    raw = await file.read()
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    imported = 0
    for row in reader:
        local_id = row["local_student_id"].strip()
        res = await db.execute(select(Student).where(Student.local_student_id == local_id))
        student = res.scalar_one_or_none()
        if not student:
            raise HTTPException(status_code=400, detail=f"Unknown local_student_id: {local_id}")

        payload = schemas.MetricIn(
            as_of_date=date.fromisoformat(row["as_of_date"]),
            attendance_percentage=float(row["attendance_percentage"]) if row.get("attendance_percentage") else None,
            growth_status=GrowthStatus(row["growth_status"]) if row.get("growth_status") else GrowthStatus.no_data,
            credits_earned=int(row["credits_earned"]) if row.get("credits_earned") else None,
            expected_credits_for_grade=int(row["expected_credits_for_grade"]) if row.get("expected_credits_for_grade") else None,
        )
        await crud.add_metric(db, student.id, payload)
        imported += 1
    return {"imported": imported}
