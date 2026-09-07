from __future__ import annotations

from db.url import resolve_database_url


def test_resolve_database_url_prefers_postgres_parts(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "mike")
    monkeypatch.setenv("POSTGRES_PASSWORD", "p@ss:word")
    monkeypatch.setenv("POSTGRES_DB", "mike_bali")
    monkeypatch.setenv("POSTGRES_HOST", "db")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert resolve_database_url() == "postgresql://mike:p%40ss%3Aword@db:5432/mike_bali"


def test_resolve_database_url_falls_back_to_database_url(monkeypatch):
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://mike@localhost:5432/mike_bali")

    assert resolve_database_url() == "postgresql://mike@localhost:5432/mike_bali"


def test_resolve_database_url_returns_none_when_unset(monkeypatch):
    for key in (
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "DATABASE_URL",
    ):
        monkeypatch.delenv(key, raising=False)

    assert resolve_database_url() is None
