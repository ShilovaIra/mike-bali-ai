from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import S3_BUCKET, S3_ENV, object_key, requires_db

CDN = S3_ENV["S3_PUBLIC_BASE_URL"]
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64


@pytest.fixture(autouse=True)
def _admin_jwt_secret(monkeypatch):
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-admin-jwt-secret-at-least-32-chars")


@asynccontextmanager
async def authed_client(store, storage):
    from admin_api.app import create_app

    await store.create_admin_user(email="admin@example.com", password="admin123")
    app = create_app(store=store, storage=storage)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        login = await client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "admin123"},
        )
        client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        yield client


def _key_from_url(url: str) -> str:
    assert url.startswith(CDN + "/")
    return url[len(CDN) + 1 :]


async def _upload(client, data: bytes, filename: str = "logo.png", content_type: str = "image/png"):
    return await client.post(
        "/api/partner-logos/uploads",
        files={"file": (filename, data, content_type)},
    )


def _bucket_keys(s3) -> list[str]:
    return sorted(item["Key"] for item in s3.list_objects_v2(Bucket=S3_BUCKET).get("Contents", []))


async def _create_partner(client) -> str:
    created = await client.post(
        "/api/partners",
        json={
            "name": "Spa Bali",
            "type": "beauty_service",
            "referral_url": "https://example.com/spa",
            "blurb": "Массаж",
            "is_active": True,
            "sort_order": 3,
        },
    )
    assert created.status_code == 201
    assert created.json()["logo_path"] == ""
    assert created.json()["logo_url"] == ""
    return created.json()["id"]


async def _link(client, partner_id: str, upload_token: str):
    return await client.put(
        f"/api/partners/{partner_id}/logo",
        json={"upload_token": upload_token},
    )


@requires_db
async def test_upload_stages_logo_under_the_env_tmp_prefix(store, asset_storage, s3):
    async with authed_client(store, asset_storage) as client:
        response = await _upload(client, PNG)

    assert response.status_code == 201
    body = response.json()
    key = _key_from_url(body["preview_url"])
    assert key.startswith(object_key("tmp/")) and key.endswith(".png")
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    assert obj["Body"].read() == PNG
    assert obj["ContentType"] == "image/png"


@requires_db
async def test_upload_rejects_non_jpeg_png_even_if_named_png(store, asset_storage, s3):
    webp = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 32
    async with authed_client(store, asset_storage) as client:
        response = await _upload(client, webp, filename="logo.png", content_type="image/png")

    assert response.status_code == 400
    assert response.json()["detail"] == "Только JPEG или PNG"
    assert _bucket_keys(s3) == []


@requires_db
async def test_link_stores_an_unprefixed_key_and_a_prefixed_object(store, asset_storage, s3):
    async with authed_client(store, asset_storage) as client:
        partner_id = await _create_partner(client)
        upload = await _upload(client, PNG)
        linked = await _link(client, partner_id, upload.json()["upload_token"])

    body = linked.json()
    assert body["logo_path"].startswith(f"partners/{partner_id}/logo-")
    assert body["logo_path"].endswith(".png")
    assert "/" + S3_ENV["S3_KEY_PREFIX"] + "/" not in f"/{body['logo_path']}"
    assert body["logo_url"] == f"{CDN}/{object_key(body['logo_path'])}"
    assert _bucket_keys(s3) == [object_key(body["logo_path"])]
    assert s3.get_object(Bucket=S3_BUCKET, Key=object_key(body["logo_path"]))["Body"].read() == PNG


@requires_db
async def test_text_update_keeps_the_linked_logo(store, asset_storage, s3):
    async with authed_client(store, asset_storage) as client:
        partner_id = await _create_partner(client)
        upload = await _upload(client, PNG)
        linked = await _link(client, partner_id, upload.json()["upload_token"])
        updated = await client.patch(
            f"/api/partners/{partner_id}",
            json={
                "name": "Spa Bali",
                "type": "beauty_service",
                "referral_url": "https://example.com/spa",
                "blurb": "Новое описание",
                "is_active": False,
                "sort_order": 4,
            },
        )

    assert updated.status_code == 200
    assert updated.json()["logo_path"] == linked.json()["logo_path"]
    assert updated.json()["is_active"] is False
    assert _bucket_keys(s3) == [object_key(linked.json()["logo_path"])]


@requires_db
async def test_relinking_deletes_the_previous_upload(store, asset_storage, s3):
    async with authed_client(store, asset_storage) as client:
        partner_id = await _create_partner(client)
        first = await _upload(client, PNG)
        first_key = (await _link(client, partner_id, first.json()["upload_token"])).json()["logo_path"]
        second = await _upload(client, JPEG, filename="logo.jpg", content_type="image/jpeg")
        relinked = (await _link(client, partner_id, second.json()["upload_token"])).json()

    assert relinked["logo_path"] != first_key
    assert relinked["logo_path"].endswith(".jpg")
    assert _bucket_keys(s3) == [object_key(relinked["logo_path"])]


@requires_db
async def test_relinking_leaves_the_bundled_file_in_the_repo(store, asset_storage, s3):
    from pathlib import Path

    bundled = Path(__file__).resolve().parents[1] / "media/partners/esim-logo.png"
    assert bundled.is_file()
    async with authed_client(store, asset_storage) as client:
        partner_id = await _create_partner(client)
        async with store.pool.acquire() as conn:
            await conn.execute(
                "UPDATE partners SET logo_path = 'media/partners/esim-logo.png' WHERE id = $1",
                partner_id,
            )
        upload = await _upload(client, PNG)
        linked = await _link(client, partner_id, upload.json()["upload_token"])

    assert bundled.is_file()
    assert _bucket_keys(s3) == [object_key(linked.json()["logo_path"])]


@requires_db
async def test_remove_logo_clears_the_partner_and_deletes_the_object(store, asset_storage, s3):
    async with authed_client(store, asset_storage) as client:
        partner_id = await _create_partner(client)
        upload = await _upload(client, PNG)
        await _link(client, partner_id, upload.json()["upload_token"])
        removed = await client.delete(f"/api/partners/{partner_id}/logo")

    assert removed.status_code == 200
    assert removed.json()["logo_path"] == ""
    assert removed.json()["logo_url"] == ""
    assert _bucket_keys(s3) == []


@requires_db
async def test_link_rejects_an_expired_upload_token(store, asset_storage, s3):
    async with authed_client(store, asset_storage) as client:
        partner_id = await _create_partner(client)
        upload = await _upload(client, PNG)
        staged_key = _key_from_url(upload.json()["preview_url"]).removeprefix(
            f"{S3_ENV['S3_KEY_PREFIX']}/"
        )
        expired = jwt.encode(
            {"purpose": "logo_upload", "key": staged_key, "exp": 1},
            "test-admin-jwt-secret-at-least-32-chars",
            algorithm="HS256",
        )
        linked = await _link(client, partner_id, expired)

    assert linked.status_code == 400
    assert linked.json()["detail"] == "Загрузка устарела, выберите файл заново"
    assert _bucket_keys(s3) == [object_key(staged_key)]


@requires_db
async def test_upload_requires_admin_login(store, asset_storage, s3):
    async with authed_client(store, asset_storage) as client:
        client.headers.pop("Authorization", None)
        response = await _upload(client, PNG)

    assert response.status_code == 401
    assert _bucket_keys(s3) == []


@requires_db
async def test_upload_reports_unconfigured_storage(store):
    async with authed_client(store, None) as client:
        response = await _upload(client, PNG)

    assert response.status_code == 503
    assert response.json()["detail"] == "Хранилище недоступно, попробуйте позже"


@requires_db
async def test_link_to_unknown_partner_leaves_no_copy(store, asset_storage, s3):
    async with authed_client(store, asset_storage) as client:
        upload = await _upload(client, PNG)
        staged = _key_from_url(upload.json()["preview_url"])
        linked = await _link(client, str(uuid4()), upload.json()["upload_token"])

    assert linked.status_code == 404
    assert _bucket_keys(s3) == [staged]
