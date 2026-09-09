from sqlalchemy import (
    Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class Observation(Base):
    __tablename__ = "observations"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    source = Column(String(32), nullable=False)  # VIIRS_NOAA20_NRT, MODIS_NRT, etc.
    satellite = Column(String(32), nullable=False)
    instrument = Column(String(32), nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    acq_datetime = Column(DateTime, nullable=False, index=True)
    frp = Column(Float, nullable=False)  # Fire Radiative Power (MW)
    brightness = Column(Float, nullable=False)  # Brightness temp (K)
    bright_t31 = Column(Float, nullable=True)
    confidence = Column(String(16), nullable=False)  # low, nominal, high, 0-100
    scan = Column(Float, default=1.0)
    track = Column(Float, default=1.0)
    daynight = Column(String(2), default="D")
    version = Column(String(16), default="1.0")
    data_quality_status = Column(String(16), default="VALID")  # VALID, SUSPECT, INVALID, DUPLICATE, QUARANTINED
    raw_hash = Column(String(64), unique=True, index=True)
    event_id = Column(String(64), ForeignKey("events.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="observations")

    __table_args__ = (
        Index("idx_obs_lat_lon_time", "latitude", "longitude", "acq_datetime"),
    )

class Event(Base):
    __tablename__ = "events"

    id = Column(String(64), primary_key=True)  # EVT-YYYYMMDD-XXXX
    status = Column(String(16), default="ACTIVE")  # ACTIVE, TERMINATED, MERGED, SPLIT
    first_seen = Column(DateTime, nullable=False, index=True)
    last_seen = Column(DateTime, nullable=False, index=True)
    duration_hours = Column(Float, default=0.0)
    observation_count = Column(Integer, default=1)
    centroid_lat = Column(Float, nullable=False, index=True)
    centroid_lon = Column(Float, nullable=False, index=True)
    convex_hull_geojson = Column(Text, nullable=True)
    area_ha = Column(Float, default=0.0)
    max_frp = Column(Float, default=0.0)
    mean_frp = Column(Float, default=0.0)
    total_fre_mj = Column(Float, default=0.0)
    frp_trend = Column(Float, default=0.0)  # slope of FRP over time

    # AI/ML & Classification
    source_class = Column(String(32), default="UNCERTAIN")
    abnormality_state = Column(String(32), default="NORMAL")  # NORMAL, ELEVATED, ABNORMAL_EXCURSION, ESCALATING, CRITICAL_FIRE
    abnormality_score = Column(Float, default=0.0)  # 0.0 to 1.0 continuous severity
    conformal_set_json = Column(Text, nullable=True)  # JSON list of classes in conformal set
    # IND_ACCIDENT, IND_NORMAL, GAS_FLARE, WILDFIRE, AGRI_BURN, MINE_HEAT, POWER_HEAT, OTHER_NATURAL, FALSE_POSITIVE, UNCERTAIN
    raw_probabilities_json = Column(Text, nullable=True)
    calibrated_prob = Column(Float, default=0.0)
    uncertainty = Column(Float, default=0.0)  # Shannon entropy / conformal metric
    abstained = Column(Boolean, default=False)
    shap_explanation_json = Column(Text, nullable=True)

    # Operational Risk & Alerting
    priority = Column(String(16), default="INFORMATIONAL")  # INFORMATIONAL, WATCH, WARNING, CRITICAL
    priority_score = Column(Float, default=0.0)

    # Industrial Association & Lineage
    nearest_facility_id = Column(String(64), ForeignKey("facilities.id"), nullable=True)
    distance_to_facility_km = Column(Float, nullable=True)
    parent_event_id = Column(String(64), nullable=True)
    lineage_type = Column(String(16), default="INITIAL")  # INITIAL, CONTINUATION, MERGE, SPLIT

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    observations = relationship("Observation", back_populates="event")
    facility = relationship("Facility", back_populates="events")
    satellite_evidence = relationship("SatelliteEvidence", back_populates="event")
    alerts = relationship("Alert", back_populates="event")
    feedback = relationship("AnalystFeedback", back_populates="event")

class Facility(Base):
    __tablename__ = "facilities"

    id = Column(String(64), primary_key=True)  # FAC-XXXXX
    name = Column(String(128), nullable=False, index=True)
    facility_type = Column(String(64), nullable=False)  # refinery, chemical, power_plant, steel, cement, etc.
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    footprint_geojson = Column(Text, nullable=True)
    source = Column(String(32), default="OSM")  # OSM, GEM, WRI, VERIFIED
    source_confidence = Column(Float, default=0.90)

    # Historical Thermal Baseline Metrics (180-day window)
    baseline_median_frp = Column(Float, default=0.0)
    baseline_mad_frp = Column(Float, default=0.0)
    baseline_p90_frp = Column(Float, default=0.0)
    baseline_p99_frp = Column(Float, default=0.0)
    baseline_obs_count = Column(Integer, default=0)
    baseline_last_updated = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)

    events = relationship("Event", back_populates="facility")

class SatelliteEvidence(Base):
    __tablename__ = "satellite_evidence"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    event_id = Column(String(64), ForeignKey("events.id"), nullable=False)
    sensor = Column(String(32), nullable=False)  # Sentinel-2, Landsat-8/9
    scene_id = Column(String(128), nullable=False)
    acquisition_time = Column(DateTime, nullable=False)
    cloud_coverage = Column(Float, default=0.0)
    status = Column(String(32), default="AVAILABLE")  # AVAILABLE, CLOUDY, NO_SCENE, PROCESSING_FAILED, NOT_REQUESTED
    ndvi = Column(Float, nullable=True)
    nbr = Column(Float, nullable=True)
    swir_anomaly = Column(Float, nullable=True)
    thumbnail_url = Column(String(256), nullable=True)
    provenance_metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="satellite_evidence")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    event_id = Column(String(64), ForeignKey("events.id"), nullable=False)
    severity = Column(String(16), nullable=False)  # INFORMATIONAL, WATCH, WARNING, CRITICAL
    status = Column(String(16), default="NEW")  # NEW, ACKNOWLEDGED, RESOLVED, SUPPRESSED
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    priority_score = Column(Float, default=0.0)
    facility_name = Column(String(128), nullable=True)
    recommended_action = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(64), nullable=True)

    event = relationship("Event", back_populates="alerts")

class AnalystFeedback(Base):
    __tablename__ = "analyst_feedback"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    event_id = Column(String(64), ForeignKey("events.id"), nullable=False)
    analyst_id = Column(String(64), nullable=False)
    verified_class = Column(String(32), nullable=False)
    confidence = Column(Float, default=1.0)
    notes = Column(Text, nullable=True)
    evidence_reviewed_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="feedback")

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    actor = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False)
    entity_type = Column(String(32), nullable=False)
    entity_id = Column(String(64), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    source = Column(String(32), nullable=False)
    status = Column(String(16), nullable=False)  # SUCCESS, FAILED, DEGRADED
    records_received = Column(Integer, default=0)
    records_valid = Column(Integer, default=0)
    records_quarantined = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)
    error_message = Column(Text, nullable=True)
