import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
import httpx
from backend.app.config import settings
from backend.app.core.logging import logger
from backend.app.core.error_codes import ErrorCode

class FIRMSValidator:
    @staticmethod
    def validate_record(record: Dict[str, Any]) -> Tuple[str, List[str]]:
        reasons = []
        lat = record.get("latitude")
        lon = record.get("longitude")
        frp = record.get("frp", 0.0)
        brightness = record.get("brightness", 300.0)

        if lat is None or lon is None:
            return "INVALID", ["missing_coordinates"]
        try:
            lat = float(lat)
            lon = float(lon)
            if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
                return "INVALID", ["coordinates_out_of_bounds"]
        except (ValueError, TypeError):
            return "INVALID", ["malformed_coordinates"]

        try:
            frp = float(frp)
            if frp < 0.0 or frp > 15000.0:
                reasons.append("impossible_frp")
        except (ValueError, TypeError):
            reasons.append("malformed_frp")

        try:
            brightness = float(brightness)
            if brightness < 200.0 or brightness > 600.0:
                reasons.append("suspect_brightness_temperature")
        except (ValueError, TypeError):
            reasons.append("malformed_brightness")

        if "acq_date" not in record and "acq_datetime" not in record:
            return "INVALID", ["missing_timestamp"]

        if "acq_date" in record and record["acq_date"] is not None:
            try:
                datetime.strptime(str(record["acq_date"]), "%Y-%m-%d")
            except (ValueError, TypeError):
                return "INVALID", ["malformed_date"]

        if reasons:
            return "SUSPECT", reasons
        return "VALID", []

    @staticmethod
    def compute_raw_hash(record: Dict[str, Any]) -> str:
        unique_str = f"{record.get('satellite')}_{record.get('latitude')}_{record.get('longitude')}_{record.get('acq_date')}_{record.get('acq_time')}_{record.get('frp')}"
        return hashlib.sha256(unique_str.encode("utf-8")).hexdigest()

class FIRMSConnector:
    def __init__(self):
        self.base_url = settings.FIRMS_BASE_URL
        self.map_key = settings.FIRMS_MAP_KEY

    async def fetch_nrt(self, source: str = "VIIRS_NOAA20_NRT", country: str = "IND", days: int = 1) -> List[Dict[str, Any]]:
        if settings.DEMO_MODE or self.map_key == "SAMPLE_FIRMS_MAP_KEY":
            logger.info("DEMO_MODE enabled or default key present. FIRMS live fetch operating in resilient fallback mode.")
            return []
        
        url = f"{self.base_url}/country/csv/{self.map_key}/{source}/{country}/{days}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    lines = resp.text.strip().splitlines()
                    if len(lines) > 1:
                        headers = lines[0].split(",")
                        records = []
                        for line in lines[1:]:
                            vals = line.split(",")
                            if len(vals) == len(headers):
                                rec = dict(zip(headers, vals))
                                records.append(rec)
                        return records
                logger.warning(f"FIRMS API returned status {resp.status_code}: {resp.text[:200]}")
                return []
        except Exception as e:
            logger.error(f"FIRMS API request error: {str(e)}", extra={"error_code": ErrorCode.FIRMS_SENSOR_UNAVAILABLE})
            return []
