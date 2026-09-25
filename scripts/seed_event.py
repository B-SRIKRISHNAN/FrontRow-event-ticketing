#!/usr/bin/env python3
"""
FrontRow Event & Seat Grid DML Seed Script
Populates deterministic seed data (1 user, 1 event, 30 seats) idempotently.
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine


def load_env_file(env_path: Path) -> dict:
    """Simple parser for .env files without external dependencies."""
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("'\"")
    return env_vars


async def seed_database(backend_dir: Path) -> int:
    env_file = backend_dir / ".env"
    env_vars = load_env_file(env_file)

    current_env = os.environ.copy()
    current_env.update(env_vars)

    db_url = current_env.get("DATABASE_URL")
    if not db_url:
        print(
            "ERROR: DATABASE_URL is not set in environment or backend/.env file.",
            file=sys.stderr,
        )
        return 1

    # Ensure asyncpg driver prefix
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"Connecting to database configuration from {env_file if env_file.exists() else 'environment'}...")
    engine = create_async_engine(db_url, echo=False)

    try:
        async with engine.begin() as conn:
            # 1. Idempotent User Creation
            user_email = "demo@frontrow.com"
            demo_password_hash = "$2b$12$CaDL5Em.nYwY7Z7y43F.MOclYRcaLTZfAbHFcfHAcheFY2No3nuJm"  # 'demo123'
            
            user_stmt = text(
                """
                INSERT INTO users (email, hashed_password, created_at)
                VALUES (:email, :hashed_password, NOW())
                ON CONFLICT (email) DO UPDATE SET hashed_password = EXCLUDED.hashed_password
                RETURNING id;
                """
            )
            res = await conn.execute(user_stmt, {"email": user_email, "hashed_password": demo_password_hash})
            user_id = res.scalar_one()
            print(f"User seeded successfully (ID: {user_id}, Email: {user_email})")

            # 2. Idempotent Event Creation
            event_title = "FrontRow Grand Concert"
            show_time = datetime.now(timezone.utc) + timedelta(days=30)

            # Check existing event
            existing_event = await conn.execute(
                text("SELECT id FROM events WHERE title = :title"),
                {"title": event_title},
            )
            event_row = existing_event.fetchone()
            if event_row:
                event_id = event_row[0]
                print(f"Event already exists (ID: {event_id}, Title: {event_title})")
            else:
                event_stmt = text(
                    """
                    INSERT INTO events (title, description, venue_name, show_time, created_at)
                    VALUES (:title, :description, :venue_name, :show_time, NOW())
                    RETURNING id;
                    """
                )
                res = await conn.execute(
                    event_stmt,
                    {
                        "title": event_title,
                        "description": "Exclusive launch concert event featuring top performers.",
                        "venue_name": "FrontRow Arena",
                        "show_time": show_time,
                    },
                )
                event_id = res.scalar_one()
                print(f"Event created successfully (ID: {event_id}, Title: {event_title})")

            # 3. Idempotent 3x10 Seat Grid Population (Rows A: $150, B: $100, C: $50)
            seat_tiers = [
                ("A", "A", 150.00),
                ("B", "B", 100.00),
                ("C", "C", 50.00),
            ]

            inserted_seats = 0
            updated_seats = 0

            for row_letter, section, price in seat_tiers:
                for seat_num in range(1, 11):
                    seat_stmt = text(
                        """
                        INSERT INTO seats (event_id, row, seat_number, section, price, status)
                        VALUES (:event_id, :row, :seat_number, :section, :price, 'AVAILABLE')
                        ON CONFLICT (event_id, row, seat_number)
                        DO UPDATE SET price = EXCLUDED.price, section = EXCLUDED.section
                        RETURNING (xmax = 0) AS is_inserted;
                        """
                    )
                    res = await conn.execute(
                        seat_stmt,
                        {
                            "event_id": event_id,
                            "row": row_letter,
                            "seat_number": seat_num,
                            "section": section,
                            "price": price,
                        },
                    )
                    is_inserted = res.scalar_one()
                    if is_inserted:
                        inserted_seats += 1
                    else:
                        updated_seats += 1

            total_seats = inserted_seats + updated_seats
            print(
                f"Seat grid seeded successfully! Total seats: {total_seats} "
                f"({inserted_seats} new inserted, {updated_seats} existing updated across Rows A, B, C)."
            )

        return 0
    except Exception as e:
        print(f"ERROR: Failed to seed event and seat data: {e}", file=sys.stderr)
        return 1
    finally:
        await engine.dispose()


def main():
    parser = argparse.ArgumentParser(description="FrontRow Event & Seat Grid DML Seed Script")
    parser.add_argument(
        "--backend-dir",
        type=Path,
        default=None,
        help="Custom path to backend directory",
    )
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    backend_dir = args.backend_dir if args.backend_dir else root_dir / "backend"

    exit_code = asyncio.run(seed_database(backend_dir))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
