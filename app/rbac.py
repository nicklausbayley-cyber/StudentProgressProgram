from fastapi import Depends, HTTPException, status
from typing import Callable
from app.models import Role
from app.deps import get_current_user  # assumes you already have this
from app.schemas import UserOut        # or whatever your current user schema is


def require_roles(*allowed: Role) -> Callable:
    """
    Usage:
      @router.get(..., dependencies=[Depends(require_roles(Role.admin))])
    or:
      def route(..., user=Depends(require_roles(Role.admin, Role.counselor)))
    """
    async def _guard(user: UserOut = Depends(get_current_user)) -> UserOut:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _guard
