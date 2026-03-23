"""Vercel Flask entrypoint: exposes `app` at repo root (see Vercel Flask docs)."""

from backend.app import app

__all__ = ["app"]
