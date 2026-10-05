from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from admin_api.deps import require_admin
from admin_api.tokens import create_access_token
from db.passwords import verify_password
from db.store import AdminUser, SessionStore
from db.url import resolve_database_url
from partner_dashboard.router import router as partner_dashboard_router
from partners import Partner, PartnerType
from stats_report import collapse_user_sources, labeled_topic_rows


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PartnerTypeIn(BaseModel):
    slug: str
    is_menu_visible: bool
    sort_order: int
    button_label: str
    topic_label: str
    intro: str
    fallback: str
    caption_emoji: str
    caption_cta: str
    button_template: str


def _partner_type_payload(partner_type: PartnerType) -> dict:
    return {
        "slug": partner_type.slug,
        "is_menu_visible": partner_type.is_menu_visible,
        "sort_order": partner_type.sort_order,
        "button_label": partner_type.button_label,
        "topic_label": partner_type.topic_label,
        "intro": partner_type.intro,
        "fallback": partner_type.fallback,
        "caption_emoji": partner_type.caption_emoji,
        "caption_cta": partner_type.caption_cta,
        "button_template": partner_type.button_template,
    }


class PartnerUserIn(BaseModel):
    email: EmailStr
    password: str
    partner_ids: list[UUID] = Field(min_length=1)


class PartnerIn(BaseModel):
    name: str
    type: str
    referral_url: str
    blurb: str = ""
    logo_path: str = ""
    is_active: bool = True
    sort_order: int = 0


def _partner_payload(partner: Partner) -> dict:
    return {
        "id": str(partner.id),
        "name": partner.name,
        "type": partner.type,
        "referral_url": partner.referral_url,
        "blurb": partner.blurb or "",
        "logo_path": partner.logo_path or "",
        "is_active": partner.is_active,
        "sort_order": partner.sort_order,
    }


def create_app(*, store: SessionStore | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        owned = False
        if store is not None:
            app.state.store = store
        else:
            database_url = resolve_database_url()
            if not database_url:
                raise RuntimeError("DATABASE_URL or POSTGRES_* is required")
            app.state.store = await SessionStore.create(database_url)
            owned = True
        yield
        if owned:
            await app.state.store.close()

    app = FastAPI(title="Mike Bali Admin API", lifespan=lifespan)
    if store is not None:
        app.state.store = store

    def _store(request: Request) -> SessionStore:
        return request.app.state.store

    @app.post("/api/auth/login", response_model=LoginResponse)
    async def login(request: Request, body: LoginRequest) -> LoginResponse:
        admin = await _store(request).get_admin_by_email(body.email)
        if admin is None or not verify_password(body.password, admin.password_hash):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")
        token = create_access_token(admin_id=admin.id, email=admin.email)
        return LoginResponse(access_token=token)

    @app.get("/api/auth/me")
    async def me(admin: AdminUser = Depends(require_admin)) -> dict:
        return {"email": admin.email}

    @app.get("/api/stats")
    async def stats(
        request: Request,
        _admin: AdminUser = Depends(require_admin),
    ) -> dict:
        store = _store(request)
        bot_stats = await store.get_bot_stats()
        partner_types = await store.list_partner_types()
        payload = asdict(bot_stats)
        payload["users_by_first_source"] = collapse_user_sources(
            bot_stats.users_by_first_source
        )
        payload["topics_all_time"] = labeled_topic_rows(
            bot_stats.topics_all_time, partner_types
        )
        payload["topics_7d"] = labeled_topic_rows(bot_stats.topics_7d, partner_types)
        return payload

    @app.get("/api/partners")
    async def list_partners(
        request: Request,
        _admin: AdminUser = Depends(require_admin),
    ) -> list[dict]:
        return [_partner_payload(item) for item in await _store(request).list_partners()]

    @app.post("/api/partners", status_code=201)
    async def create_partner(
        request: Request,
        body: PartnerIn,
        _admin: AdminUser = Depends(require_admin),
    ) -> dict:
        created = await _store(request).create_partner(
            name=body.name,
            type=body.type,
            referral_url=body.referral_url,
            blurb=body.blurb,
            logo_path=body.logo_path,
            is_active=body.is_active,
            sort_order=body.sort_order,
        )
        return _partner_payload(created)

    @app.patch("/api/partners/{partner_id}")
    async def update_partner(
        request: Request,
        partner_id: UUID,
        body: PartnerIn,
        _admin: AdminUser = Depends(require_admin),
    ) -> dict:
        try:
            updated = await _store(request).update_partner(
                partner_id,
                name=body.name,
                type=body.type,
                referral_url=body.referral_url,
                blurb=body.blurb,
                logo_path=body.logo_path,
                is_active=body.is_active,
                sort_order=body.sort_order,
            )
        except KeyError:
            raise HTTPException(status_code=404, detail="Партнёр не найден") from None
        return _partner_payload(updated)

    @app.get("/api/partner-types")
    async def list_partner_types(
        request: Request,
        _admin: AdminUser = Depends(require_admin),
    ) -> list[dict]:
        return [
            _partner_type_payload(item)
            for item in await _store(request).list_partner_types()
        ]

    @app.post("/api/partner-types", status_code=201)
    async def create_partner_type(
        request: Request,
        body: PartnerTypeIn,
        _admin: AdminUser = Depends(require_admin),
    ) -> dict:
        created = await _store(request).create_partner_type(
            slug=body.slug,
            is_menu_visible=body.is_menu_visible,
            sort_order=body.sort_order,
            button_label=body.button_label,
            topic_label=body.topic_label,
            intro=body.intro,
            fallback=body.fallback,
            caption_emoji=body.caption_emoji,
            caption_cta=body.caption_cta,
            button_template=body.button_template,
        )
        return _partner_type_payload(created)

    @app.patch("/api/partner-types/{slug}")
    async def update_partner_type(
        request: Request,
        slug: str,
        body: PartnerTypeIn,
        _admin: AdminUser = Depends(require_admin),
    ) -> dict:
        try:
            updated = await _store(request).update_partner_type(
                slug,
                is_menu_visible=body.is_menu_visible,
                sort_order=body.sort_order,
                button_label=body.button_label,
                topic_label=body.topic_label,
                intro=body.intro,
                fallback=body.fallback,
                caption_emoji=body.caption_emoji,
                caption_cta=body.caption_cta,
                button_template=body.button_template,
            )
        except KeyError:
            raise HTTPException(status_code=404, detail="Тип партнёра не найден") from None
        return _partner_type_payload(updated)

    @app.get("/api/partner-users")
    async def list_partner_users(
        request: Request,
        _admin: AdminUser = Depends(require_admin),
    ) -> list[dict]:
        return await _store(request).list_partner_users()

    @app.post("/api/partner-users", status_code=201)
    async def create_partner_user(
        request: Request,
        body: PartnerUserIn,
        _admin: AdminUser = Depends(require_admin),
    ) -> dict:
        if await _store(request).get_admin_by_email(body.email):
            raise HTTPException(status_code=409, detail="Email уже используется")
        user_id, email = await _store(request).create_partner_user(
            email=body.email,
            password=body.password,
            partner_ids=body.partner_ids,
        )
        return {"id": str(user_id), "email": email}

    @app.delete("/api/partner-users/{partner_user_id}", status_code=204)
    async def delete_partner_user(
        request: Request,
        partner_user_id: UUID,
        _admin: AdminUser = Depends(require_admin),
    ) -> None:
        deleted = await _store(request).delete_partner_user(partner_user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

    app.include_router(partner_dashboard_router)
    return app
