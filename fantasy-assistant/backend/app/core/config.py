"""Configuration settings for the application."""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    postgres_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/fantasy"
    
    # Cache
    redis_url: str = "redis://cache:6379/0"
    
    # API Keys (optional, will use CSV fallbacks if not provided)
    projections_api_key: str = ""
    injuries_api_key: str = ""
    llm_api_key: str = ""
    
    # Draft sync (optional)
    sleeper_league_id: str = ""
    
    # Scoring configuration
    scoring_json: str = '{"pass_yd":0.04,"pass_td":4,"int":-2,"rush_yd":0.1,"rush_td":6,"rec":1,"rec_yd":0.1,"rec_td":6,"fumble":-2}'
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]
    ALLOWED_ORIGINS: list[str] = ["*"]
    
    # Environment
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()