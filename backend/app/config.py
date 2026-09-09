from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "THERMALIS-X"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "thermalis-dev-secret-key-change-in-production-sha256-minimum-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    DATABASE_URL: str = "sqlite:///./thermalis.db"

    # External APIs
    FIRMS_BASE_URL: str = "https://firms.modaps.eosdis.nasa.gov/api"
    FIRMS_MAP_KEY: str = "SAMPLE_FIRMS_MAP_KEY"
    FIRMS_CACHE_TTL_SECONDS: int = 3600
    WEATHER_BASE_URL: str = "https://api.open-meteo.com/v1"
    STAC_API_URL: str = "https://earth-search.aws.element84.com/v1"
    OVERPASS_URL: str = "https://overpass-api.de/api/interpreter"

    # Event & Spatiotemporal Parameters
    SPATIAL_CLUSTER_RADIUS_KM: float = 1.25
    TEMPORAL_WINDOW_HOURS: float = 24.0
    BASELINE_WINDOW_DAYS: int = 180
    ALERT_COOLDOWN_MINUTES: int = 60
    UNCERTAINTY_THRESHOLD_ENTROPY: float = 0.60
    UNCERTAINTY_THRESHOLD_MARGIN: float = 0.15

    # Modes
    DEMO_MODE: bool = True
    REAL_DATA_MODE: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
