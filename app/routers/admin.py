from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app import crud
from app.models import Role
from app.schemas import UserCreate, UserOut
from app.rbac import require_roles

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", response_model=UserOut, dependencies=[Depends(require_roles(Role.admin))])
async def create_user_admin_only(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.create_user(db, payload)
