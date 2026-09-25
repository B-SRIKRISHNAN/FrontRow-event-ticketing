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


def get_python_interpreter(backend_dir: Path) -> str:
    """Find Python interpreter with alembic installed, preferring backend/.venv if present."""
    venv_win = backend_dir / ".venv" / "Scripts" / "python.exe"
    if venv_win.exists():
        return str(venv_win)
    venv_nix = backend_dir / ".venv" / "bin" / "python"
    if venv_nix.exists():
        return str(venv_nix)
    return sys.executable


def run_migrations(revision: str = "head", downgrade: bool = False, backend_dir: Path | None = None) -> int:
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

    action = "downgrade" if downgrade or revision == "base" else "upgrade"
    print(f"Connecting to database configuration from {backend_dir / '.env' if env_file.exists() else 'environment'}...")
    print(f"Running Alembic migration {action} to '{revision}'...")

    python_bin = get_python_interpreter(backend_dir)
    # Programmatic alembic command script executed via the target python interpreter
    py_code = (
        "import os, sys; "
        "from alembic.config import Config; "
        "from alembic import command; "
        "cfg = Config('alembic.ini'); "
        f"command.{action}(cfg, '{revision}')"
    )
    cmd = [python_bin, "-c", py_code]

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
        "--downgrade",
        action="store_true",
        help="Perform migration downgrade to target revision",
    )
    parser.add_argument(
        "--backend-dir",
        type=Path,
        default=None,
        help="Custom path to backend directory",
    )
    args = parser.parse_args()

    sys.exit(run_migrations(revision=args.revision, downgrade=args.downgrade, backend_dir=args.backend_dir))


if __name__ == "__main__":
    main()
