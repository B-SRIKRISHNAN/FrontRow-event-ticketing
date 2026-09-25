import os
from pathlib import Path
from pydantic import BaseModel


def load_env_file(env_path: Path) -> dict:
    env_vars = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip("'\"")
    return env_vars


# Load backend/.env
backend_dir = Path(__file__).resolve().parent.parent
env_vars = load_env_file(backend_dir / ".env")
for k, v in env_vars.items():
    os.environ.setdefault(k, v)


class Settings(BaseModel):
    PROJECT_NAME: str = "FrontRow Event Ticketing Core API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/frontrow",
    )
    # Ensure asyncpg prefix
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_frontrow_jwt_key_change_in_prod_12345")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    HOLD_DURATION_SECONDS: int = int(os.getenv("HOLD_DURATION_SECONDS", "300"))  # 5 minutes

    # Connection pool configuration for main request engine
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "15"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))

    # Connection pool configuration for sweeper worker
    SWEEPER_POOL_SIZE: int = int(os.getenv("SWEEPER_POOL_SIZE", "2"))
    SWEEPER_INTERVAL_SECONDS: int = int(os.getenv("SWEEPER_INTERVAL_SECONDS", "15"))


settings = Settings()
