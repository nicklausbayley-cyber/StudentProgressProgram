from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import date
from app import models, schemas
from app.security import hash_password
from app.rules import evaluate_rules, RuleInput

async def create_user(db: AsyncSession, data: schemas.UserCreate) -> models.User:
    user = models.User(
        email=data.email.lower().strip(),
        hashed_password=hash_password(data.password),
        role=data.role,
        student_id=data.student_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str):
    res = await db.execute(select(models.User).where(models.User.email == email.lower().strip()))
    return res.scalar_one_or_none()

async def create_student(db: AsyncSession, data: schemas.StudentCreate) -> models.Student:
    student = models.Student(**data.model_dump())
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student

async def list_students(db: AsyncSession, limit: int = 100, offset: int = 0):
    res = await db.execute(select(models.Student).order_by(models.Student.last_name, models.Student.first_name).limit(limit).offset(offset))
    return res.scalars().all()

async def get_student(db: AsyncSession, student_id: int):
    res = await db.execute(select(models.Student).where(models.Student.id == student_id))
    return res.scalar_one_or_none()

async def add_metric(db: AsyncSession, student_id: int, data: schemas.MetricIn) -> models.StudentMetric:
    inp = RuleInput(
        attendance_percentage=data.attendance_percentage,
        growth_status=data.growth_status,
        credits_earned=data.credits_earned,
        expected_credits_for_grade=data.expected_credits_for_grade,
    )
    out = evaluate_rules(inp)

    metric = models.StudentMetric(
        student_id=student_id,
        as_of_date=data.as_of_date,
        attendance_percentage=data.attendance_percentage,
        growth_status=data.growth_status,
        credits_earned=data.credits_earned,
        expected_credits_for_grade=data.expected_credits_for_grade,
        attendance_risk_flag=out.attendance_risk_flag,
        academic_risk_flag=out.academic_risk_flag,
        graduation_risk_flag=out.graduation_risk_flag,
        risk_flag_count=out.risk_flag_count,
        student_status=out.student_status,
        intervention_required=out.intervention_required,
    )
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric

async def latest_metric_for_student(db: AsyncSession, student_id: int):
    res = await db.execute(
        select(models.StudentMetric)
        .where(models.StudentMetric.student_id == student_id)
        .order_by(desc(models.StudentMetric.as_of_date))
        .limit(1)
    )
    return res.scalar_one_or_none()

async def log_action(db: AsyncSession, actor_user_id: int | None, action: str, target_type: str | None = None, target_id: str | None = None):
    db.add(models.AuditLog(actor_user_id=actor_user_id, action=action, target_type=target_type, target_id=target_id))
    await db.commit()
