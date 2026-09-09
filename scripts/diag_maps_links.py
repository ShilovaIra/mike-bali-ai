"""Live check that Mike never sends a dead Google Maps link.

Replays restaurant -> "send me a maps link" dialogues through the bot's real
answer pipeline (prompt, find_places tool, sanitizer), extracts every URL from
the answer, and resolves it over HTTP. Exits 1 if any link is dead.

Costs OpenAI and Places calls, so run it by hand after touching MIKE_PROMPT,
places.py or maps_links.py; the unit tests cover the rest.

    python scripts/diag_maps_links.py --runs 4       # expect 0 dead
    python scripts/diag_maps_links.py --no-places    # without the Places tool
    python scripts/diag_maps_links.py --baseline     # current prompt, no sanitizer
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

import bot  # noqa: E402

# Real dialogues a Tourist would hit asking for a Google Maps link.
CASES = [
    [
        "💬 \nСпросить Майка",
        "посоветуй ресторан в Чангу",
        "отправь ссылку на этот ресторан в гугл картах",
    ],
    [
        "💬 \nСпросить Майка",
        "где выпить кофе в Убуде?",
        "отправь ссылку на это кафе в гугл картах",
    ],
]

URL_RE = re.compile(r"https?://[^\s<>()\[\]\"'`,]+")


def _sanitize(answer: str) -> str:
    sanitize = getattr(bot, "sanitize_map_links", None)
    if sanitize is None:
        return answer
    return sanitize(answer)


async def ask(turns: list[str], *, baseline: bool) -> str:
    """Replay a multi-turn dialogue through the bot's own answer pipeline."""
    prompt = bot.MIKE_PROMPT if baseline else bot.system_prompt()
    messages: list[dict] = [{"role": "system", "content": prompt}]
    answer = ""
    for turn in turns:
        messages.append({"role": "user", "content": turn})
        if baseline:
            response = await asyncio.to_thread(
                bot.client.responses.create,
                model="gpt-4.1-mini",
                input=messages,
            )
            answer = response.output_text
        else:
            answer = _sanitize(await bot.run_model(messages))
        messages.append({"role": "assistant", "content": answer})
    return answer


def check_url(url: str) -> tuple[bool, str]:
    """A link is good only if it resolves to a live page."""
    url = url.rstrip(".,;:!?)")
    try:
        response = requests.get(
            url,
            timeout=20,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (diag-maps-links)"},
        )
    except requests.RequestException as exc:
        return False, f"unreachable: {type(exc).__name__}"

    if response.status_code >= 400:
        return False, f"HTTP {response.status_code}"
    if "consent.google.com" in response.url or "google.com/maps" in response.url:
        return True, f"HTTP {response.status_code} -> maps"
    return True, f"HTTP {response.status_code} -> {response.url[:70]}"


async def run_cases(runs: int, *, baseline: bool) -> int:
    total = dead = no_link = 0
    for run in range(runs):
        for index, turns in enumerate(CASES):
            answer = await ask(turns, baseline=baseline)
            urls = URL_RE.findall(answer)
            print(f"\n=== run {run + 1} case {index + 1} ===")
            print(answer.strip()[:600])
            if not urls:
                no_link += 1
                print("  !! no URL in answer")
                continue
            for url in urls:
                total += 1
                ok, detail = check_url(url)
                if not ok:
                    dead += 1
                print(f"  [{'OK  ' if ok else 'DEAD'}] {url}  ({detail})")

    print(f"\nlinks={total} dead={dead} answers_without_link={no_link}")
    return 1 if dead else 0


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-places", action="store_true", help="answer without the Places tool"
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="current prompt only, no sanitizer and no tool loop",
    )
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    if args.baseline:
        print("baseline: raw MIKE_PROMPT, no sanitizer, no Places tool")
        return await run_cases(args.runs, baseline=True)

    key = os.getenv("GOOGLE_PLACES_API_KEY")
    if args.no_places or not key:
        if not args.no_places:
            print("!! GOOGLE_PLACES_API_KEY not set — running without place lookups")
        return await run_cases(args.runs, baseline=False)

    from places import PlacesClient  # noqa: E402

    bot.places = PlacesClient(key)
    try:
        return await run_cases(args.runs, baseline=False)
    finally:
        await bot.places.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
