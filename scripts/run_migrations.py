#!/usr/bin/env python3
"""
FrontRow Database Migration Runner Script
Executes Alembic migrations cleanly across Windows, Linux, and macOS.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


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


def run_migrations(revision: str = "head", backend_dir: Path | None = None) -> int:
    root_dir = Path(__file__).resolve().parent.parent
    if backend_dir is None:
        backend_dir = root_dir / "backend"

    env_file = backend_dir / ".env"
    env_vars = load_env_file(env_file)

    # Combine process environment with backend .env variables
    current_env = os.environ.copy()
    current_env.update(env_vars)

    db_url = current_env.get("DATABASE_URL")
    if not db_url:
        print(
            "ERROR: DATABASE_URL is not set in environment or backend/.env file.",
            file=sys.stderr,
        )
        print(
            "Please copy backend/.env.example to backend/.env and configure your database settings.",
            file=sys.stderr,
        )
        return 1

    print(f"Connecting to database configuration from {backend_dir / '.env' if env_file.exists() else 'environment'}...")
    print(f"Running Alembic migration upgrade to '{revision}'...")

    cmd = [sys.executable, "-m", "alembic", "upgrade", revision]
    try:
        result = subprocess.run(cmd, cwd=backend_dir, env=current_env, check=True)
        print("Database migrations applied successfully.")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Alembic migration failed with exit code {e.returncode}", file=sys.stderr)
        return e.returncode
    except Exception as e:
        print(f"ERROR: Failed to run migration script: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="FrontRow Alembic Migration Runner")
    parser.add_argument(
        "--revision",
        default="head",
        help="Alembic target revision (default: 'head')",
    )
    parser.add_argument(
        "--backend-dir",
        type=Path,
        default=None,
        help="Custom path to backend directory",
    )
    args = parser.parse_args()

    sys.exit(run_migrations(revision=args.revision, backend_dir=args.backend_dir))


if __name__ == "__main__":
    main()
