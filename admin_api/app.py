from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import asdict
from uuid import UUID

import asyncpg
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field

from admin_api.deps import require_admin
from admin_api.tokens import create_access_token
from admin_api.webapp import telegram_user
from db.passwords import verify_password
from db.store import AdminUser, SessionStore
from knowledge_base import KnowledgeBaseEntry
from db.url import resolve_database_url
from maps_links import sanitize_map_links
from partner_dashboard.offers import wrap_partners_for_channel_user, wrap_partners_for_user
from partner_dashboard.router import router as partner_dashboard_router
from partners import (
    PACKAGE_ROOT,
    Partner,
    PartnerType,
    build_partner_button_text,
    partner_type_chip,
    resolve_logo_path,
)
from stats_report import collapse_user_sources, labeled_topic_rows
from tourist_answers import answer_with_partner_list, choose_partner_type as default_choose_partner_type
from tourist_answers import write_tourist_answer


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


class KnowledgeBaseIn(BaseModel):
    partner_id: UUID


class TmaMessageIn(BaseModel):
    text: str


def _knowledge_base_payload(entry: KnowledgeBaseEntry) -> dict:
    return {
        "id": str(entry.id),
        "partner_id": str(entry.partner_id),
        "name": entry.name,
        "kind": entry.kind,
        "blurb": entry.blurb,
        "referral_url": entry.referral_url,
        "in_chat": entry.is_visible,
    }


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


def _tma_partner_payload(partner: Partner, partner_type: PartnerType | None) -> dict:
    action = partner.name
    type_label = partner.type
    if partner_type is not None:
        action = build_partner_button_text(partner, partner_type)
        type_label = partner_type_chip(partner_type.topic_label)
    return {
        "id": str(partner.id),
        "name": partner.name,
        "blurb": partner.blurb or "",
        "type_label": type_label,
        "action": action,
        "logo_url": f"/api/tma/partners/{partner.id}/logo" if partner.logo_path else "",
    }


def create_app(
    *,
    store: SessionStore | None = None,
    choose_partner_type: Callable[[str, list[str]], Awaitable[str | None]] | None = None,
    write_answer: Callable[[str], Awaitable[str]] | None = None,
) -> FastAPI:
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

    @app.get("/api/partners/{partner_id}/logo")
    async def partner_logo(
        request: Request,
        partner_id: UUID,
        _admin: AdminUser = Depends(require_admin),
    ) -> FileResponse:
        partner = next(
            (
                item
                for item in await _store(request).list_partners()
                if item.id == partner_id
            ),
            None,
        )
        path = resolve_logo_path(partner.logo_path) if partner else None
        media_dir = (PACKAGE_ROOT / "media" / "partners").resolve()
        if path is None or not path.resolve().is_relative_to(media_dir):
            raise HTTPException(status_code=404, detail="Логотип не найден")
        return FileResponse(path)

    @app.get("/api/knowledge-base")
    async def list_knowledge_base(
        request: Request,
        _admin: AdminUser = Depends(require_admin),
    ) -> list[dict]:
        entries = await _store(request).list_knowledge_base()
        return [_knowledge_base_payload(entry) for entry in entries]

    @app.post("/api/knowledge-base", status_code=201)
    async def add_knowledge_base_entry(
        request: Request,
        body: KnowledgeBaseIn,
        _admin: AdminUser = Depends(require_admin),
    ) -> dict:
        try:
            entry = await _store(request).add_knowledge_base_partner(body.partner_id)
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=409, detail="Уже в базе знаний") from None
        return _knowledge_base_payload(entry)

    @app.delete("/api/knowledge-base/{entry_id}", status_code=204)
    async def delete_knowledge_base_entry(
        request: Request,
        entry_id: UUID,
        _admin: AdminUser = Depends(require_admin),
    ) -> None:
        await _store(request).delete_knowledge_base_entry(entry_id)

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

    async def require_tourist(request: Request) -> dict:
        header = request.headers.get("authorization", "")
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        user = None
        if header.startswith("tma "):
            user = telegram_user(header.removeprefix("tma ").strip(), token)
        if user is None:
            raise HTTPException(status_code=401, detail="Нужна подпись Telegram")
        return user

    @app.get("/api/tma/me")
    async def tma_me(tourist: dict = Depends(require_tourist)) -> dict:
        return {
            "first_name": str(tourist.get("first_name") or ""),
            "last_name": str(tourist.get("last_name") or ""),
            "photo_url": str(tourist.get("photo_url") or ""),
        }

    @app.get("/api/tma/messages")
    async def list_tma_messages(
        request: Request,
        tourist: dict = Depends(require_tourist),
    ) -> list[dict]:
        return await _store(request).list_thread_messages("telegram", str(tourist["id"]))

    @app.post("/api/tma/messages")
    async def post_tma_message(
        request: Request,
        body: TmaMessageIn,
        tourist: dict = Depends(require_tourist),
    ) -> dict:
        text = body.text.strip()
        session = _store(request)
        telegram_id = str(tourist["id"])
        types = await session.list_partner_types()
        chooser = choose_partner_type or default_choose_partner_type
        chosen = await chooser(text, [item.slug for item in types])
        partner_type = next((item for item in types if item.slug == chosen), None)
        active = (
            await session.list_active_partners(partner_type.slug)
            if partner_type is not None
            else []
        )
        if partner_type is not None and active:
            reply = await answer_with_partner_list(session, telegram_id, text, partner_type)
            return {"reply": reply}
        await session.append_message("telegram", telegram_id, role="user", content=text)
        if write_answer is None:
            reply = await write_tourist_answer(session, telegram_id)
        else:
            reply = await write_answer(text)
        lead_ready = "ЗАЯВКА_ГОТОВА" in reply
        reply = sanitize_map_links(reply.replace("ЗАЯВКА_ГОТОВА", "").strip())
        await session.append_message(
            "telegram", telegram_id, role="assistant", content=reply
        )
        if lead_ready:
            history = await session.get_ai_context("telegram", telegram_id, limit=16)
            username = tourist.get("username")
            await session.create_lead(
                "telegram",
                telegram_id,
                snapshot={
                    "telegram_id": telegram_id,
                    "telegram_username": f"@{username}" if username else None,
                    "telegram_first_name": tourist.get("first_name"),
                    "dialogue": history,
                },
            )
        return {"reply": reply}

    @app.get("/api/tma/favorites")
    async def list_tma_favorites(
        request: Request,
        tourist: dict = Depends(require_tourist),
    ) -> list[dict]:
        saved = await _store(request).list_saved_partners("telegram", str(tourist["id"]))
        types = {item.slug: item for item in await _store(request).list_partner_types()}
        return [_tma_partner_payload(partner, types.get(partner.type)) for partner in saved]

    @app.put("/api/tma/favorites/{partner_id}")
    async def save_tma_favorite(
        request: Request,
        partner_id: UUID,
        tourist: dict = Depends(require_tourist),
    ) -> dict:
        await _store(request).save_partner("telegram", str(tourist["id"]), partner_id)
        return {"id": str(partner_id)}

    @app.delete("/api/tma/favorites/{partner_id}", status_code=204)
    async def forget_tma_favorite(
        request: Request,
        partner_id: UUID,
        tourist: dict = Depends(require_tourist),
    ) -> None:
        await _store(request).forget_partner("telegram", str(tourist["id"]), partner_id)

    @app.post("/api/tma/partners/{partner_id}/open")
    async def open_tma_partner(request: Request, partner_id: UUID) -> dict:
        header = request.headers.get("authorization", "")
        visitor_id = ""
        tourist: dict | None = None
        if header.startswith("tma "):
            tourist = await require_tourist(request)
        else:
            visitor_id = request.headers.get("x-visitor-id", "").strip()
            if not visitor_id:
                raise HTTPException(status_code=401, detail="Нужна подпись Telegram")
        session = _store(request)
        partner = next(
            (
                item
                for item in await session.list_partners()
                if item.id == partner_id and item.is_active
            ),
            None,
        )
        if partner is None:
            raise HTTPException(status_code=404, detail="Партнёр не найден")
        public_base = os.environ.get("PARTNER_OFFER_BASE_URL", "")
        if tourist is not None:
            wrapped = await wrap_partners_for_channel_user(
                session,
                [partner],
                "telegram",
                str(tourist["id"]),
                public_base=public_base,
            )
        else:
            user_id = await session.ensure_user("tma", visitor_id, source="tma")
            wrapped = await wrap_partners_for_user(
                session.pool,
                [partner],
                user_id,
                public_base=public_base,
            )
        url = wrapped[0].referral_url
        base = public_base.strip().rstrip("/")
        if not (base.startswith("http://") or base.startswith("https://")) or not url.startswith(
            f"{base}/r/"
        ):
            raise HTTPException(status_code=503, detail="Ссылка недоступна")
        return {"url": url}

    @app.get("/api/tma/partners")
    async def list_tma_partners(request: Request) -> list[dict]:
        partners = await _store(request).list_partners()
        types = {item.slug: item for item in await _store(request).list_partner_types()}
        return [
            _tma_partner_payload(partner, types.get(partner.type))
            for partner in partners
            if partner.is_active
        ]

    @app.get("/api/tma/partners/{partner_id}/logo")
    async def tma_partner_logo(request: Request, partner_id: UUID) -> FileResponse:
        partner = next(
            (
                item
                for item in await _store(request).list_partners()
                if item.id == partner_id and item.is_active
            ),
            None,
        )
        path = resolve_logo_path(partner.logo_path) if partner else None
        media_dir = (PACKAGE_ROOT / "media" / "partners").resolve()
        if path is None or not path.resolve().is_relative_to(media_dir):
            raise HTTPException(status_code=404, detail="Логотип не найден")
        return FileResponse(path)

    app.include_router(partner_dashboard_router)
    return app
