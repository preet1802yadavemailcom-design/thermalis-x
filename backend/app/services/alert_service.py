from datetime import datetime
from typing import Dict, Any, Optional

class AlertService:
    @staticmethod
    def generate_alert_payload(event: Dict[str, Any], priority: str, priority_score: float, facility_name: str = None) -> Optional[Dict[str, Any]]:
        # Only issue formal alerts for WATCH, WARNING, CRITICAL
        if priority not in ["WATCH", "WARNING", "CRITICAL"]:
            return None

        event_id = event.get("id")
        source_class = event.get("source_class")
        frp_max = event.get("max_frp")

        if priority == "CRITICAL":
            title = f"CRITICAL: Confirmed Industrial Fire Excursion at {facility_name or 'Industrial Zone'}"
            action = "Immediate dispatch of industrial disaster management team. Activate facility emergency shutdown protocols."
        elif priority == "WARNING":
            title = f"WARNING: Abnormal High-FRP Thermal Signature at {facility_name or 'Nearby Industrial Cluster'}"
            action = "Task urgent high-resolution satellite/optical verification. Request ground confirmation from site control officer."
        else:
            title = f"WATCH: Persistent Thermal Anomaly Monitored near {facility_name or 'Facility'}"
            action = "Log event in analyst review queue. Monitor subsequent satellite passes for perimeter dilation."

        desc = f"Event {event_id} exhibits max FRP of {frp_max} MW, classified as {source_class} with priority score {priority_score}/100."

        return {
            "event_id": event_id,
            "severity": priority,
            "title": title,
            "description": desc,
            "priority_score": priority_score,
            "facility_name": facility_name,
            "recommended_action": action,
            "status": "NEW"
        }
