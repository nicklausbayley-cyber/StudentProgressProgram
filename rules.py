from dataclasses import dataclass
from typing import Optional
from app.models import GrowthStatus, StudentStatus

ATTENDANCE_THRESHOLD = 94.0

@dataclass
class RuleInput:
    attendance_percentage: Optional[float]
    growth_status: GrowthStatus
    credits_earned: Optional[int]
    expected_credits_for_grade: Optional[int]

@dataclass
class RuleOutput:
    attendance_risk_flag: bool
    academic_risk_flag: bool
    graduation_risk_flag: bool
    risk_flag_count: int
    student_status: StudentStatus
    intervention_required: bool

def evaluate_rules(inp: RuleInput) -> RuleOutput:
    attendance_risk_flag = False
    academic_risk_flag = False
    graduation_risk_flag = False

    # Attendance Rule
    if inp.attendance_percentage is not None and inp.attendance_percentage < ATTENDANCE_THRESHOLD:
        attendance_risk_flag = True

    # Growth Rule
    if inp.growth_status == GrowthStatus.below:
        academic_risk_flag = True

    # Graduation / Credit Pace Rule
    if (
        inp.credits_earned is not None
        and inp.expected_credits_for_grade is not None
        and inp.credits_earned < inp.expected_credits_for_grade
    ):
        graduation_risk_flag = True

    risk_flag_count = sum([attendance_risk_flag, academic_risk_flag, graduation_risk_flag])

    if risk_flag_count == 0:
        student_status = StudentStatus.on_track
    elif risk_flag_count == 1:
        student_status = StudentStatus.watch
    elif risk_flag_count == 2:
        student_status = StudentStatus.at_risk
    else:
        student_status = StudentStatus.high_risk

    intervention_required = risk_flag_count >= 2

    return RuleOutput(
        attendance_risk_flag=attendance_risk_flag,
        academic_risk_flag=academic_risk_flag,
        graduation_risk_flag=graduation_risk_flag,
        risk_flag_count=risk_flag_count,
        student_status=student_status,
        intervention_required=intervention_required,
    )
