import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    team_name: str = os.getenv("TEAM_NAME", "Magicpin Challenge")
    contact_email: str = os.getenv("CONTACT_EMAIL", "example@email.com")
    model_name: str = os.getenv("MODEL_NAME", "Context Aware Merchant AI")
    approach: str = os.getenv(
        "APPROACH",
        "Rule Engine + Context Store + Mock LLM",
    )
    version: str = os.getenv("APP_VERSION", "1.0")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
