from __future__ import annotations

from partner_logo_migration import migrate_bundled_logos
from tests.conftest import S3_BUCKET, object_key, requires_db


@requires_db
async def test_bundled_logos_move_under_the_env_prefix(store, asset_storage, s3):
    partner = await store.create_partner(
        name="eSIM",
        type="esim",
        referral_url="https://example.com/esim",
        logo_path="media/partners/esim-logo.png",
        sort_order=1,
    )

    report = await migrate_bundled_logos(store, asset_storage)

    assert [item.source for item in report.migrated] == ["media/partners/esim-logo.png"]
    saved = next(item for item in await store.list_partners() if item.id == partner.id)
    assert saved.logo_path.startswith(f"partners/{partner.id}/logo-")
    assert not saved.logo_path.startswith("test/")
    body = s3.get_object(Bucket=S3_BUCKET, Key=object_key(saved.logo_path))["Body"].read()
    assert body.startswith(b"\x89PNG")

    second = await migrate_bundled_logos(store, asset_storage)
    assert second.migrated == []
    again = next(item for item in await store.list_partners() if item.id == partner.id)
    assert again.logo_path == saved.logo_path


@requires_db
async def test_missing_bundled_file_is_reported_and_skipped(store, asset_storage, s3, tmp_path):
    partner = await store.create_partner(
        name="Spa",
        type="beauty_service",
        referral_url="https://example.com/spa",
        logo_path="media/partners/missing-logo.png",
        sort_order=1,
    )

    report = await migrate_bundled_logos(store, asset_storage, root=tmp_path)

    assert [item.partner_id for item in report.missing] == [partner.id]
    saved = next(item for item in await store.list_partners() if item.id == partner.id)
    assert saved.logo_path == "media/partners/missing-logo.png"
    assert s3.list_objects_v2(Bucket=S3_BUCKET).get("Contents", []) == []
