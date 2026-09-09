import httpx
from typing import Dict, Any
from backend.app.config import settings
from backend.app.core.logging import logger

class WeatherService:
    @staticmethod
    async def get_weather(lat: float, lon: float) -> Dict[str, Any]:
        url = f"{settings.WEATHER_BASE_URL}/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json().get("current", {})
                    return {
                        "temperature_2m": data.get("temperature_2m", 28.0),
                        "relative_humidity_2m": data.get("relative_humidity_2m", 50.0),
                        "wind_speed_10m": data.get("wind_speed_10m", 12.0),
                        "wind_direction_10m": data.get("wind_direction_10m", 180.0)
                    }
        except Exception as e:
            logger.warning(f"Weather API unavailable, using climatological default: {str(e)}")
        
        return {
            "temperature_2m": 29.5,
            "relative_humidity_2m": 52.0,
            "wind_speed_10m": 14.2,
            "wind_direction_10m": 215.0
        }
