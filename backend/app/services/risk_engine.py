from typing import Dict, Any, Tuple

class RiskPriorityEngine:
    @staticmethod
    def calculate_priority(
        source_class: str,
        calibrated_prob: float,
        frp_max: float,
        facility_type: str = "none",
        uncertainty: float = 0.0
    ) -> Tuple[str, float]:
        # 1. Likelihood weight
        is_accident = (source_class == "IND_ACCIDENT")
        p_weight = calibrated_prob if is_accident else (0.05 * calibrated_prob)

        # 2. Thermal severity (0 to 1, scaled by 400 MW)
        s_therm = min(1.0, frp_max / 400.0)

        # 3. Facility criticality: full criticality applies to accidents; normal operations scale down
        criticality_map = {
            "refinery": 1.0,
            "petrochemical": 1.0,
            "chemical": 0.95,
            "power_plant": 0.85,
            "steel": 0.75,
            "ceramic_manufacturing": 0.60,
            "coal_mine": 0.50,
            "none": 0.10
        }
        base_criticality = criticality_map.get(facility_type, 0.2)
        c_fac = base_criticality if is_accident else (base_criticality * 0.20)

        # Weighted calculation (sum = 100)
        # 50% accident likelihood, 30% thermal magnitude, 20% facility criticality
        raw_score = (50.0 * p_weight) + (30.0 * s_therm) + (20.0 * c_fac)

        # Discount by uncertainty
        priority_score = raw_score * (1.0 - 0.4 * uncertainty)
        priority_score = round(max(5.0, min(99.0, priority_score)), 1)

        if priority_score >= 75.0:
            category = "CRITICAL"
        elif priority_score >= 55.0:
            category = "WARNING"
        elif priority_score >= 30.0:
            category = "WATCH"
        else:
            category = "INFORMATIONAL"

        return category, priority_score

    @staticmethod
    def calculate_evacuation_and_response(
        priority_category: str,
        facility_type: str,
        frp_max: float,
        wind_speed_kmh: float = 12.0,
        wind_direction_deg: float = 180.0
    ) -> Dict[str, Any]:
        """
        Computes Emergency Response Guide (ERG 2024) isolation distance, downwind
        hazard plume corridor, and multi-agency escalation routing for industrial fires.
        """
        if priority_category == "CRITICAL":
            isolation_radius_m = 1500 if facility_type in ["refinery", "petrochemical"] else 800
            downwind_corridor_km = round((isolation_radius_m / 1000.0) * max(1.5, wind_speed_kmh / 10.0), 2)
            agencies = [
                "District Disaster Management Authority (DDMA)",
                "State Disaster Management Authority (SDMA)",
                "National Disaster Response Force (NDRF)",
                "Fire & Emergency Services (Foam Units)",
                "Petroleum and Explosives Safety Organization (PESO)"
            ]
            action = "IMMEDIATE EVACUATION & LEVEL-3 HAZMAT FOAM SUPPRESSION"
        elif priority_category == "WARNING":
            isolation_radius_m = 500
            downwind_corridor_km = round((isolation_radius_m / 1000.0) * max(1.2, wind_speed_kmh / 12.0), 2)
            agencies = [
                "Industrial Area Mutual Aid Scheme (MACS)",
                "District Fire & Rescue Services",
                "State Pollution Control Board (SPCB)"
            ]
            action = "CORDON PERIMETER & TASK SATELLITE OPTICAL RECONNAISSANCE"
        elif priority_category == "WATCH":
            isolation_radius_m = 150
            downwind_corridor_km = 0.5
            agencies = [
                "Facility Safety Officer",
                "SPCB Regional Officer"
            ]
            action = "CONTINUOUS CEMS & THERMAL SATELLITE SURVEILLANCE"
        else:
            isolation_radius_m = 50
            downwind_corridor_km = 0.1
            agencies = [
                "Facility Routine Operations Staff"
            ]
            action = "NORMAL OPERATIONS LOGGING - NO EMERGENCY DISPATCH"

        downwind_azimuth = (wind_direction_deg + 180.0) % 360.0

        return {
            "priority_category": priority_category,
            "isolation_radius_meters": isolation_radius_m,
            "downwind_protective_action_distance_km": downwind_corridor_km,
            "downwind_dispersion_azimuth_deg": round(downwind_azimuth, 1),
            "recommended_action": action,
            "dispatched_agencies": agencies,
            "regulatory_standard": "NDMA Chemical (Industrial) Disaster SOP & ERG 2024 Table 1"
        }

    @staticmethod
    def generate_ics_201_brief(event_data: Dict[str, Any], response_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates an official Incident Command System (ICS Form 201) Incident Briefing
        standardized according to National Disaster Management Authority (NDMA)
        and US FEMA / ERG 2024 Incident Command Guidelines.
        """
        event_id = event_data.get("id", "UNKNOWN")
        source_class = event_data.get("source_class", "UNKNOWN")
        priority = event_data.get("priority", "UNKNOWN")
        priority_score = event_data.get("priority_score", 0.0)
        facility_name = event_data.get("nearest_facility_name") or "Off-site / Unregistered Land Parcel"
        lat = event_data.get("centroid_lat", 0.0)
        lon = event_data.get("centroid_lon", 0.0)
        max_frp = event_data.get("max_frp", 0.0)
        abnormality = event_data.get("abnormality_state", "NORMAL")
        abnormality_score = event_data.get("abnormality_score", 0.0)

        briefing_text = (
            f"=== ICS-201 INCIDENT BRIEFING ===\n"
            f"INCIDENT NAME: THERMALIS-{event_id}\n"
            f"MAP / SKETCH COORDINATES: {lat:.5f} N, {lon:.5f} E\n"
            f"PRIMARY FACILITY: {facility_name}\n"
            f"CLASSIFICATION: {source_class} (ABNORMALITY: {abnormality}, Z-SCORE: {abnormality_score:.2f})\n"
            f"INCIDENT PRIORITY: {priority} (SCORE: {priority_score:.1f}/100)\n"
            f"MAX RADIATIVE POWER: {max_frp:.1f} MW\n"
            f"INITIAL RESPONSE OBJECTIVE: {response_plan.get('recommended_action')}\n"
            f"MANDATORY ISOLATION PERIMETER: {response_plan.get('isolation_radius_meters')} meters\n"
            f"DOWNWIND HAZARD CORRIDOR: {response_plan.get('downwind_protective_action_distance_km')} km at heading {response_plan.get('downwind_dispersion_azimuth_deg')}°\n"
            f"DESIGNATED DISPATCH AGENCIES: {', '.join(response_plan.get('dispatched_agencies', []))}\n"
            f"GOVERNING STANDARD: {response_plan.get('regulatory_standard')}\n"
            f"================================="
        )

        return {
            "form_type": "ICS-201 Incident Briefing",
            "incident_name": f"THERMALIS-{event_id}",
            "coordinates": {"lat": lat, "lon": lon},
            "facility_name": facility_name,
            "situation_summary": {
                "source_class": source_class,
                "abnormality_state": abnormality,
                "abnormality_score": abnormality_score,
                "max_frp_mw": max_frp,
                "priority": priority,
                "priority_score": priority_score
            },
            "initial_objectives": response_plan.get("recommended_action"),
            "safety_perimeters": {
                "initial_isolation_radius_meters": response_plan.get("isolation_radius_meters"),
                "protective_action_corridor_km": response_plan.get("downwind_protective_action_distance_km"),
                "downwind_azimuth_deg": response_plan.get("downwind_dispersion_azimuth_deg")
            },
            "assigned_resources": response_plan.get("dispatched_agencies", []),
            "governing_standard": response_plan.get("regulatory_standard"),
            "formatted_briefing": briefing_text
        }

