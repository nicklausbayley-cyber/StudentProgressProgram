from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app import crud
from app.models import Role
from app.schemas import UserCreate, UserOut
from app.rbac import require_roles
from app.deps import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post(
    "/users",
    response_model=UserOut,
    dependencies=[Depends(require_roles(Role.admin, Role.counselor))],
)
async def create_user_admin_or_counselor(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    # Counselors can create users, but cannot create admins.
    if current_user.role == Role.counselor and payload.role == Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Counselors cannot create admin users",
        )

    return await crud.create_user(db, payload)
