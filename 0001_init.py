"""init

Revision ID: 0001_init
Revises: 
Create Date: 2026-01-12

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("local_student_id", sa.String(length=64), nullable=False),
        sa.Column("first_name", sa.String(length=80), nullable=False),
        sa.Column("last_name", sa.String(length=80), nullable=False),
        sa.Column("grade_level", sa.Integer(), nullable=False),
        sa.Column("diploma_path", sa.String(length=80), nullable=True),
    )
    op.create_index("ix_students_local_student_id", "students", ["local_student_id"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("admin","counselor","student", name="role"), nullable=False),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "student_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("attendance_percentage", sa.Float(), nullable=True),
        sa.Column("growth_status", sa.Enum("exceeds","meets","below","no_data", name="growthstatus"), nullable=False, server_default="no_data"),
        sa.Column("credits_earned", sa.Integer(), nullable=True),
        sa.Column("expected_credits_for_grade", sa.Integer(), nullable=True),

        sa.Column("attendance_risk_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("academic_risk_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("graduation_risk_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("risk_flag_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("student_status", sa.Enum("on_track","watch","at_risk","high_risk", name="studentstatus"), nullable=False, server_default="on_track"),
        sa.Column("intervention_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),

        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.UniqueConstraint("student_id","as_of_date", name="uq_student_asof"),
    )
    op.create_index("ix_student_metrics_student_id", "student_metrics", ["student_id"])
    op.create_index("ix_student_metrics_as_of_date", "student_metrics", ["as_of_date"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=200), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=True),
        sa.Column("target_id", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])

def downgrade() -> None:
    op.drop_index("ix_audit_logs_actor_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_student_metrics_as_of_date", table_name="student_metrics")
    op.drop_index("ix_student_metrics_student_id", table_name="student_metrics")
    op.drop_table("student_metrics")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_students_local_student_id", table_name="students")
    op.drop_table("students")
