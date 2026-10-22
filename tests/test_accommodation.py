"""A ready rent of a place to live is filed, and the user never sees the hidden phrase."""

from __future__ import annotations

from accommodation import Stay, settle_reply


def test_ready_rent_is_filed_as_arenda_without_the_hidden_phrase():
    reply = (
        "Записал: аренда в Чангу, бюджет 15 млн, две спальни, заезд в ноябре. "
        "Имя Анна, WhatsApp +62 812. Передам команде.\n"
        "ЗАЯВКА_ГОТОВА"
    )

    settlement = settle_reply(reply, Stay(deal="rent"))

    assert settlement.file_lead is True
    assert settlement.title == "Аренда"
    assert settlement.home is None
    assert "ЗАЯВКА_ГОТОВА" not in settlement.text
    assert "Чангу" in settlement.text


def test_named_villa_buy_is_filed_as_pokupka_with_the_villa():
    reply = "Записал покупку виллы в Убуде.\nЗАЯВКА_ГОТОВА"

    settlement = settle_reply(reply, Stay(deal="buy", home="villa"))

    assert settlement.file_lead is True
    assert settlement.title == "Покупка"
    assert settlement.home == "вилла"
    assert "ЗАЯВКА_ГОТОВА" not in settlement.text


def test_a_rejected_handoff_shows_only_the_refusal():
    reply = "Передал заявку на отель команде.\nЗАЯВКА_ГОТОВА"

    settlement = settle_reply(reply, None)

    assert settlement.file_lead is False
    assert settlement.title is None
    assert settlement.home is None
    assert (
        settlement.text
        == "Беру заявки только на аренду или покупку виллы, квартиры, дома или комнаты."
    )


def test_a_leaked_phrase_on_a_guide_answer_is_dropped_without_a_lead():
    reply = "Лучший пляж в Чангу — Берава.\nЗАЯВКА_ГОТОВА"

    settlement = settle_reply(reply, None)

    assert settlement.file_lead is False
    assert settlement.title is None
    assert settlement.home is None
    assert settlement.text == "Лучший пляж в Чангу — Берава."


def test_a_rent_that_also_refuses_a_job_keeps_the_reply_and_files():
    reply = (
        "Беру заявки только на аренду или покупку виллы, квартиры, дома или комнаты. "
        "Сколько спален нужно?\n"
        "ЗАЯВКА_ГОТОВА"
    )

    settlement = settle_reply(reply, Stay(deal="rent"))

    assert settlement.file_lead is True
    assert settlement.title == "Аренда"
    assert settlement.home is None
    assert "Сколько спален нужно?" in settlement.text
    assert "Беру заявки только" in settlement.text
    assert "ЗАЯВКА_ГОТОВА" not in settlement.text
