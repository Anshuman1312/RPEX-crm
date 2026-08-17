#!/usr/bin/env python3
"""
Initialize core system roles in the database.

Usage:
    cd backend
    python scripts/init_roles.py
"""

from __future__ import annotations

import asyncio
import sys

from app.database.init_db import init_roles_only
from app.core.logging import setup_logging


async def main() -> None:
    """Initialize roles."""
    setup_logging()
    try:
        await init_roles_only()
        print("✓ System roles initialized successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Failed to initialize roles: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
