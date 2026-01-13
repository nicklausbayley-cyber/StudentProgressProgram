from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/student_risk"
    jwt_secret: str = "change-me"
    jwt_expires_minutes: int = 120
    cors_origins: str = ""

    def cors_origin_list(self) -> List[str]:
        if not self.cors_origins.strip():
            return []
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
