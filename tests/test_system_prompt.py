"""What Mike is told to say when someone wants a hotel or a job."""

from __future__ import annotations

from bot import system_prompt

REFUSAL = "Беру заявки только на аренду или покупку виллы, квартиры, дома или комнаты."


def test_an_opening_hotel_or_job_is_only_the_refusal():
    prompt = system_prompt()

    assert REFUSAL in prompt
    assert "Если чат начинается с отеля или работы" in prompt
    assert "не задавай ни одного вопроса" in prompt
    assert "Весь ответ — только эта фраза" in prompt


def test_a_hotel_or_job_during_a_rent_or_buy_continues_with_the_home():
    prompt = system_prompt()

    assert (
        "Если во время аренды или покупки просят отель или работу, скажи эту фразу"
        in prompt
    )
    assert "затем задай следующий вопрос про жильё" in prompt


def test_a_hotel_name_used_as_a_landmark_still_gets_a_guide_answer():
    prompt = system_prompt()

    assert "Название отеля как ориентир — не запрос отеля" in prompt
    assert "отвечай на сам вопрос" in prompt
