from __future__ import annotations

from partners import Partner, is_bundled_logo
from storage import AssetStorage


def partner_payload(partner: Partner, storage: AssetStorage | None) -> dict:
    logo = partner.logo_path or ""
    logo_url = ""
    if logo and storage is not None and not is_bundled_logo(logo):
        logo_url = storage.public_url(logo)
    return {
        "id": str(partner.id),
        "name": partner.name,
        "type": partner.type,
        "referral_url": partner.referral_url,
        "blurb": partner.blurb or "",
        "logo_path": logo,
        "logo_url": logo_url,
        "is_active": partner.is_active,
        "sort_order": partner.sort_order,
    }
