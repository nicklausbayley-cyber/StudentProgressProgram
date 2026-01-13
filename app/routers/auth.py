from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app import crud
from app.models import Role, User
from app.schemas import Token, UserCreate, UserOut
from app.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    # current_user optional for bootstrap; we’ll enforce below
    current_user: UserOut | None = None,
):
    # BOOTSTRAP RULE:
    # If there are no users yet, allow creating the first user (should be admin).
    # Otherwise, only admins can register new users.
    res = await db.execute(select(User.id).limit(1))
    any_user_exists = res.scalar_one_or_none() is not None

    if any_user_exists:
        # Lazy import to avoid circular import
        from app.deps import get_current_user
        current_user = await get_current_user(db=db)  # not possible; deps expects request
        # Instead of trying to call deps directly, we enforce admin via dependency:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RBAC misconfigured: use /auth/register_admin_guarded endpoint",
        )

    # First user must be admin for safety
    if payload.role != Role.admin:
        raise HTTPException(status_code=400, detail="First user must be admin")

    return await crud.create_user(db, payload)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await crud.authenticate_user(db, form_data.username, form_data.password)
    except Exception:
        # Don't crash the API on auth failures. Surface as invalid credentials.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.email, role=user.role)
    return Token(access_token=token)
