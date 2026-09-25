#!/usr/bin/env python3
"""
FrontRow One-Shot Initialization & Services Runner Script
Automates environment setup, database migrations, DML data seeding, and multi-service process orchestration.
"""

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

# Base Paths
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
LLM_DIR = ROOT_DIR / "llm-engine"
FRONTEND_DIR = ROOT_DIR / "frontend"
SCRIPTS_DIR = ROOT_DIR / "scripts"


def load_env_file(env_path: Path) -> dict:
    """Parse key-value pairs from a .env file without external dependencies."""
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("'\"")
    return env_vars


def verify_env_files() -> bool:
    """Verify that required .env files exist in each service directory before execution."""
    required_envs = [
        (BACKEND_DIR / ".env", BACKEND_DIR / ".env.example"),
        (LLM_DIR / ".env", LLM_DIR / ".env.example"),
        (FRONTEND_DIR / ".env", FRONTEND_DIR / ".env.example"),
    ]

    print("=== Step 1: Environment Verification ===")
    missing_count = 0

    for env_file, example_file in required_envs:
        rel_env = env_file.relative_to(ROOT_DIR)
        rel_example = example_file.relative_to(ROOT_DIR)

        if env_file.exists():
            print(f"  [OK] {rel_env} found.")
        else:
            print(f"  [MISSING] {rel_env} is missing!")
            print(f"            Please copy {rel_example} to {rel_env} and configure required environment variables.")
            missing_count += 1

    if missing_count > 0:
        print(f"\nERROR: {missing_count} required .env file(s) missing.", file=sys.stderr)
        print("Please set up all required environment files before running the initialization script.", file=sys.stderr)
        return False

    print("All environment files verified successfully.\n")
    return True


def check_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a TCP port is currently bound/in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0


def verify_database_connection() -> bool:
    """Pre-flight check to verify PostgreSQL database reachability."""
    backend_env = load_env_file(BACKEND_DIR / ".env")
    db_url = os.environ.get("DATABASE_URL") or backend_env.get("DATABASE_URL", "")

    if not db_url:
        print("ERROR: DATABASE_URL is not defined in environment or backend/.env.", file=sys.stderr)
        return False

    # Extract host and port from DATABASE_URL if standard format
    # format: postgresql+asyncpg://user:pass@host:port/dbname
    try:
        if "@" in db_url:
            host_port_part = db_url.split("@")[1].split("/")[0]
            if ":" in host_port_part:
                host, port_str = host_port_part.split(":", 1)
                port = int(port_str)
            else:
                host = host_port_part
                port = 5432
        else:
            host = "127.0.0.1"
            port = 5432

        # Check raw TCP connection to PostgreSQL server
        if not check_port_in_use(port, host):
            print(
                f"ERROR: Cannot connect to PostgreSQL database service at {host}:{port}.",
                file=sys.stderr,
            )
            print(
                "Please ensure your PostgreSQL database service is running and accessible.",
                file=sys.stderr,
            )
            return False
        return True
    except Exception as e:
        print(f"WARNING: Database connection check parsing failed: {e}. Proceeding...", file=sys.stderr)
        return True


def get_python_interpreter(service_dir: Path | None = None) -> str:
    """Find Python interpreter with installed dependencies, checking venv directories."""
    dirs_to_check = []
    if service_dir:
        dirs_to_check.append(service_dir)
    dirs_to_check.extend([BACKEND_DIR, LLM_DIR, ROOT_DIR])

    for d in dirs_to_check:
        venv_win = d / ".venv" / "Scripts" / "python.exe"
        if venv_win.exists():
            return str(venv_win)
        venv_nix = d / ".venv" / "bin" / "python"
        if venv_nix.exists():
            return str(venv_nix)

    return sys.executable


def run_migrations() -> bool:
    """Execute Alembic database migrations via run_migrations.py."""
    print("=== Step 2: Database Migrations ===")
    migration_script = SCRIPTS_DIR / "run_migrations.py"
    if not migration_script.exists():
        print(f"ERROR: Migration script {migration_script} not found.", file=sys.stderr)
        return False

    py_bin = get_python_interpreter(BACKEND_DIR)
    cmd = [py_bin, str(migration_script)]
    try:
        res = subprocess.run(cmd, cwd=ROOT_DIR)
        if res.returncode != 0:
            print("ERROR: Database migration failed.", file=sys.stderr)
            return False
        print()
        return True
    except Exception as e:
        print(f"ERROR: Failed to run migrations: {e}", file=sys.stderr)
        return False


def run_seed_data() -> bool:
    """Execute DML event and seat grid seeding via seed_event.py."""
    print("=== Step 3: DML Seed Data Population ===")
    seed_script = SCRIPTS_DIR / "seed_event.py"
    if not seed_script.exists():
        print(f"ERROR: Seed script {seed_script} not found.", file=sys.stderr)
        return False

    py_bin = get_python_interpreter(BACKEND_DIR)
    cmd = [py_bin, str(seed_script)]
    try:
        res = subprocess.run(cmd, cwd=ROOT_DIR)
        if res.returncode != 0:
            print("ERROR: Data seeding failed.", file=sys.stderr)
            return False
        print()
        return True
    except Exception as e:
        print(f"ERROR: Failed to run seed script: {e}", file=sys.stderr)
        return False


def get_uv_binary(service_dir: Path) -> Path | None:
    """Find uv binary inside the service virtual environment or global PATH."""
    uv_win = service_dir / ".venv" / "Scripts" / "uv.exe"
    if uv_win.exists():
        return uv_win
    uv_nix = service_dir / ".venv" / "bin" / "uv"
    if uv_nix.exists():
        return uv_nix
    global_uv = shutil.which("uv")
    if global_uv:
        return Path(global_uv)
    return None


def ensure_dependencies() -> bool:
    """Bootstrap virtual environments, install venv-local uv, and run uv sync for backend & llm-engine."""
    print("=== Step 0: Dependency Bootstrapping ===")

    # 1. Backend venv + uv sync
    backend_venv = BACKEND_DIR / ".venv"
    if not backend_venv.exists():
        print("  [BOOTSTRAP] Creating virtual environment in backend/.venv...")
        res = subprocess.run([sys.executable, "-m", "venv", str(backend_venv)], cwd=BACKEND_DIR)
        if res.returncode != 0:
            print("ERROR: Failed to create backend virtual environment.", file=sys.stderr)
            return False

    backend_py = get_python_interpreter(BACKEND_DIR)
    backend_uv = get_uv_binary(BACKEND_DIR)

    if not backend_uv:
        print("  [BOOTSTRAP] Installing 'uv' inside backend/.venv...")
        res = subprocess.run([backend_py, "-m", "pip", "install", "uv"], cwd=BACKEND_DIR)
        if res.returncode != 0:
            print("ERROR: Failed to install uv in backend/.venv.", file=sys.stderr)
            return False
        backend_uv = get_uv_binary(BACKEND_DIR)

    print("  [BOOTSTRAP] Synchronizing dependencies via 'uv sync' in backend/...")
    res = subprocess.run([str(backend_uv), "sync"], cwd=BACKEND_DIR)
    if res.returncode != 0:
        print("ERROR: 'uv sync' failed in backend/.", file=sys.stderr)
        return False
    print("  [OK] Backend dependencies synchronized.")

    # 2. LLM Engine venv + uv sync
    llm_venv = LLM_DIR / ".venv"
    if not llm_venv.exists():
        print("  [BOOTSTRAP] Creating virtual environment in llm-engine/.venv...")
        res = subprocess.run([sys.executable, "-m", "venv", str(llm_venv)], cwd=LLM_DIR)
        if res.returncode != 0:
            print("ERROR: Failed to create llm-engine virtual environment.", file=sys.stderr)
            return False

    llm_py = get_python_interpreter(LLM_DIR)
    llm_uv = get_uv_binary(LLM_DIR)

    if not llm_uv:
        print("  [BOOTSTRAP] Installing 'uv' inside llm-engine/.venv...")
        res = subprocess.run([llm_py, "-m", "pip", "install", "uv"], cwd=LLM_DIR)
        if res.returncode != 0:
            print("ERROR: Failed to install uv in llm-engine/.venv.", file=sys.stderr)
            return False
        llm_uv = get_uv_binary(LLM_DIR)

    print("  [BOOTSTRAP] Synchronizing dependencies via 'uv sync' in llm-engine/...")
    res = subprocess.run([str(llm_uv), "sync"], cwd=LLM_DIR)
    if res.returncode != 0:
        print("ERROR: 'uv sync' failed in llm-engine/.", file=sys.stderr)
        return False
    print("  [OK] LLM Engine dependencies synchronized.")

    # 3. Frontend node_modules
    frontend_modules = FRONTEND_DIR / "node_modules"
    if not frontend_modules.exists():
        print("  [BOOTSTRAP] Installing Frontend npm packages (node_modules)...")
        npm_bin = "npm.cmd" if sys.platform == "win32" else "npm"
        res = subprocess.run([npm_bin, "install"], cwd=FRONTEND_DIR)
        if res.returncode != 0:
            print("ERROR: Failed to install Frontend npm packages.", file=sys.stderr)
            return False
    else:
        print("  [OK] Frontend npm packages ready.")

    print("All service dependencies bootstrapped successfully.\n")
    return True


def start_services():
    """Spawn Backend, LLM Engine, and Frontend processes concurrently in dedicated console windows."""
    print("=== Step 4: Starting Microservices ===")

    services = [
        {"name": "Backend API", "port": 8000, "dir": BACKEND_DIR},
        {"name": "LLM Engine", "port": 8001, "dir": LLM_DIR},
        {"name": "Frontend App", "port": 3000, "dir": FRONTEND_DIR},
    ]

    # Pre-flight port check
    conflicts = []
    for srv in services:
        if check_port_in_use(srv["port"]):
            conflicts.append(f"  - {srv['name']} (Port {srv['port']} is already in use)")

    if conflicts:
        print("WARNING: Port conflicts detected:")
        for conf in conflicts:
            print(conf)
        print("The services will attempt to run, but port conflicts may cause startup failures.")
        print()

    backend_py = get_python_interpreter(BACKEND_DIR)
    llm_py = get_python_interpreter(LLM_DIR)

    backend_cmd = [backend_py, "-m", "uvicorn", "app.main:app", "--port", "8000", "--reload"]
    llm_cmd = [llm_py, "-m", "uvicorn", "app.main:app", "--port", "8001", "--reload"]

    npm_bin = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_cmd = [npm_bin, "run", "dev"]

    popen_kwargs = {}
    if sys.platform == "win32":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE

    processes = []
    try:
        print("Launching Backend API (:8000) in dedicated console window...")
        p_backend = subprocess.Popen(backend_cmd, cwd=BACKEND_DIR, **popen_kwargs)
        processes.append(("Backend API", p_backend))

        print("Launching LLM Engine (:8001) in dedicated console window...")
        p_llm = subprocess.Popen(llm_cmd, cwd=LLM_DIR, **popen_kwargs)
        processes.append(("LLM Engine", p_llm))

        print("Launching Frontend App (:3000) in dedicated console window...")
        p_frontend = subprocess.Popen(frontend_cmd, cwd=FRONTEND_DIR, **popen_kwargs)
        processes.append(("Frontend App", p_frontend))

        print()
        print("==========================================================")
        print("  FrontRow Services Successfully Started!")
        print("  - Backend API:  http://localhost:8000 (Swagger: /docs)")
        print("  - LLM Engine:   http://localhost:8001 (Health: /health)")
        print("  - Frontend App: http://localhost:3000")
        print("==========================================================")
        print("Press Ctrl+C to stop all services.")
        print()

        while True:
            time.sleep(1)
            # Check if any child process crashed prematurely
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"WARNING: Service {name} exited with code {proc.returncode}.")

    except KeyboardInterrupt:
        print("\nStopping FrontRow services...")
        for name, proc in processes:
            if proc.poll() is None:
                print(f"Terminating {name}...")
                proc.terminate()
        time.sleep(1)
        for name, proc in processes:
            if proc.poll() is None:
                proc.kill()
        print("All FrontRow services stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="FrontRow One-Shot Initialization & Microservice Runner",
    )
    parser.add_argument("--skip-env", action="store_true", help="Skip creating .env files from templates")
    parser.add_argument("--skip-migrations", action="store_true", help="Skip running database migrations")
    parser.add_argument("--skip-seed", action="store_true", help="Skip database DML seeding")
    parser.add_argument("--skip-services", action="store_true", help="Skip launching microservices")

    args = parser.parse_args()

    print("==========================================================")
    print("      FrontRow One-Shot Initialization & Runner         ")
    print("==========================================================")
    print()

    # 0. Dependency Bootstrapping
    if not ensure_dependencies():
        sys.exit(1)

    # 1. Environment files verification
    if not args.skip_env:
        if not verify_env_files():
            sys.exit(1)

    # Pre-flight DB check
    if not args.skip_migrations or not args.skip_seed:
        if not verify_database_connection():
            print("Initialization halted due to database reachability failure.", file=sys.stderr)
            sys.exit(1)

    # 2. Database migrations
    if not args.skip_migrations:
        if not run_migrations():
            print("Initialization halted due to migration failure.", file=sys.stderr)
            sys.exit(1)

    # 3. Data seeding
    if not args.skip_seed:
        if not run_seed_data():
            print("Initialization halted due to seed failure.", file=sys.stderr)
            sys.exit(1)

    # 4. Launch services
    if not args.skip_services:
        start_services()
    else:
        print("Initialization complete (--skip-services specified).")


if __name__ == "__main__":
    main()
