from sqlalchemy import String, Integer, Date, Enum, ForeignKey, UniqueConstraint, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
import enum
from typing import Optional, List

class Role(str, enum.Enum):
    admin = "admin"
    counselor = "counselor"
    student = "student"

class GrowthStatus(str, enum.Enum):
    exceeds = "EXCEEDS"
    meets = "MEETS"
    below = "BELOW"
    no_data = "NO_DATA"

class StudentStatus(str, enum.Enum):
    on_track = "ON_TRACK"
    watch = "WATCH"
    at_risk = "AT_RISK"
    high_risk = "HIGH_RISK"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.student)
    student_id: Mapped[Optional[int]] = mapped_column(ForeignKey("students.id"), nullable=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped[Optional["Student"]] = relationship(back_populates="user")

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    local_student_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    grade_level: Mapped[int] = mapped_column(Integer)  # 6-12 etc
    diploma_path: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)

    user: Mapped[Optional[User]] = relationship(back_populates="student")
    metrics: Mapped[List["StudentMetric"]] = relationship(back_populates="student", cascade="all, delete-orphan")

class StudentMetric(Base):
    __tablename__ = "student_metrics"
    __table_args__ = (UniqueConstraint("student_id", "as_of_date", name="uq_student_asof"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)

    as_of_date: Mapped[Date] = mapped_column(Date, index=True)

    attendance_percentage: Mapped[Optional[float]] = mapped_column(nullable=True)  # 0-100
    growth_status: Mapped[GrowthStatus] = mapped_column(Enum(GrowthStatus), default=GrowthStatus.no_data)
    credits_earned: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expected_credits_for_grade: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # computed flags / outputs (stored for auditability; recompute any time)
    attendance_risk_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    academic_risk_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    graduation_risk_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    risk_flag_count: Mapped[int] = mapped_column(Integer, default=0)
    student_status: Mapped[StudentStatus] = mapped_column(Enum(StudentStatus), default=StudentStatus.on_track)
    intervention_required: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    student: Mapped["Student"] = relationship(back_populates="metrics")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(200))
    target_type: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    target_id: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
