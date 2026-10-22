from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stay:
    deal: str
    home: str | None = None


@dataclass(frozen=True)
class Settlement:
    text: str
    file_lead: bool
    title: str | None
    home: str | None


REFUSAL = "Беру заявки только на аренду или покупку виллы, квартиры, дома или комнаты."


def settle_reply(reply: str, stay: Stay | None) -> Settlement:
    text = reply.replace("ЗАЯВКА_ГОТОВА", "").strip()
    if stay is None:
        if _claims_request_was_sent(text):
            text = REFUSAL
        return Settlement(text=text, file_lead=False, title=None, home=None)
    return Settlement(
        text=text,
        file_lead=True,
        title="Аренда" if stay.deal == "rent" else "Покупка",
        home="вилла" if stay.home == "villa" else None,
    )


def _claims_request_was_sent(text: str) -> bool:
    return "заявк" in text.lower()
