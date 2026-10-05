from __future__ import annotations

from typing import Optional
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

from admin_api.tokens import decode_access_token
from partner_dashboard.offers import record_referral_click
from partner_dashboard.store import (
    PartnerUser,
    authenticate_partner_user,
    get_partner_stats,
    get_partner_user_by_email,
    has_partner_access,
    list_accessible_partners,
)
from partner_dashboard.tokens import create_partner_access_token

bearer_scheme = HTTPBearer(auto_error=False)

router = APIRouter()


class PartnerLoginRequest(BaseModel):
    email: EmailStr
    password: str


class PartnerLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _store(request: Request):
    return request.app.state.store


async def require_partner_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> PartnerUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
        if payload.get("role") != "partner_user":
            raise HTTPException(status_code=401, detail="Invalid token")
        email = str(payload["email"])
    except HTTPException:
        raise
    except (jwt.PyJWTError, KeyError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token") from None

    user = await get_partner_user_by_email(_store(request).pool, email)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.post("/api/partner/auth/login", response_model=PartnerLoginResponse)
async def partner_login(request: Request, body: PartnerLoginRequest) -> PartnerLoginResponse:
    user = authenticate_partner_user(
        await get_partner_user_by_email(_store(request).pool, body.email),
        body.password,
    )
    if user is None:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if not await list_accessible_partners(_store(request).pool, user.id):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = create_partner_access_token(partner_user_id=user.id, email=user.email)
    return PartnerLoginResponse(access_token=token)


@router.get("/api/partner/me")
async def partner_me(
    request: Request,
    user: PartnerUser = Depends(require_partner_user),
) -> dict:
    partners = await list_accessible_partners(_store(request).pool, user.id)
    return {"email": user.email, "partners": partners}


@router.get("/api/partner/stats")
async def partner_stats(
    request: Request,
    partner_id: UUID,
    user: PartnerUser = Depends(require_partner_user),
) -> dict:
    if not await has_partner_access(
        _store(request).pool, partner_user_id=user.id, partner_id=partner_id
    ):
        raise HTTPException(status_code=404, detail="Партнёр не найден")
    return await get_partner_stats(_store(request).pool, partner_id)


@router.get("/r/{token}")
async def follow_wrapped_offer(request: Request, token: str) -> RedirectResponse:
    url = await record_referral_click(_store(request).pool, token)
    if url is None:
        raise HTTPException(status_code=404, detail="Not found")
    return RedirectResponse(url=url, status_code=302)
