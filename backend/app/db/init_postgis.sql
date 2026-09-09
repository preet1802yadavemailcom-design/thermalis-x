-- THERMALIS-X Production PostGIS Initialization & Spatial Schema DDL
-- Smart India Hackathon Problem Statement 26162

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Facilities Entity Table
CREATE TABLE IF NOT EXISTS facilities (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(64) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    centroid_geom GEOMETRY(Point, 4326),
    polygon_geom GEOMETRY(Polygon, 4326),
    footprint_geojson TEXT,
    area_sqm DOUBLE PRECISION,
    hazop_tier VARCHAR(32) DEFAULT 'TIER_2',
    has_active_flaring_consent BOOLEAN DEFAULT FALSE,
    baseline_median_frp DOUBLE PRECISION DEFAULT 0.0,
    baseline_mad_frp DOUBLE PRECISION DEFAULT 1.0,
    baseline_p90_frp DOUBLE PRECISION DEFAULT 0.0,
    baseline_obs_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_facilities_centroid ON facilities USING GIST (centroid_geom);
CREATE INDEX IF NOT EXISTS idx_facilities_polygon ON facilities USING GIST (polygon_geom);
CREATE INDEX IF NOT EXISTS idx_facilities_type ON facilities (facility_type);

-- 2. Spatiotemporal Events Entity Table
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(64) PRIMARY KEY,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    first_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    last_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_hours DOUBLE PRECISION DEFAULT 0.0,
    observation_count INTEGER DEFAULT 1,
    centroid_lat DOUBLE PRECISION NOT NULL,
    centroid_lon DOUBLE PRECISION NOT NULL,
    centroid_geom GEOMETRY(Point, 4326),
    hull_geom GEOMETRY(Polygon, 4326),
    convex_hull_geojson TEXT,
    area_ha DOUBLE PRECISION DEFAULT 0.5,
    max_frp DOUBLE PRECISION NOT NULL,
    mean_frp DOUBLE PRECISION NOT NULL,
    total_fre_mj DOUBLE PRECISION DEFAULT 0.0,
    frp_trend DOUBLE PRECISION DEFAULT 0.0,
    source_class VARCHAR(64) NOT NULL,
    abnormality_state VARCHAR(64) NOT NULL DEFAULT 'NORMAL',
    abnormality_score DOUBLE PRECISION DEFAULT 0.0,
    raw_probabilities_json TEXT,
    conformal_set_json TEXT,
    calibrated_prob DOUBLE PRECISION NOT NULL,
    uncertainty DOUBLE PRECISION NOT NULL,
    abstained BOOLEAN DEFAULT FALSE,
    priority VARCHAR(32) NOT NULL,
    priority_score DOUBLE PRECISION NOT NULL,
    nearest_facility_id VARCHAR(64) REFERENCES facilities(id),
    distance_to_facility_km DOUBLE PRECISION,
    lineage_type VARCHAR(32) DEFAULT 'INITIAL',
    parent_event_id VARCHAR(64),
    shap_explanation_json TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_centroid ON events USING GIST (centroid_geom);
CREATE INDEX IF NOT EXISTS idx_events_hull ON events USING GIST (hull_geom);
CREATE INDEX IF NOT EXISTS idx_events_status ON events (status);
CREATE INDEX IF NOT EXISTS idx_events_priority ON events (priority);
CREATE INDEX IF NOT EXISTS idx_events_temporal ON events (first_seen, last_seen);

-- 3. Satellite Active Fire Observations Table
CREATE TABLE IF NOT EXISTS observations (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) REFERENCES events(id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    point_geom GEOMETRY(Point, 4326),
    brightness DOUBLE PRECISION NOT NULL,
    scan DOUBLE PRECISION DEFAULT 0.38,
    track DOUBLE PRECISION DEFAULT 0.36,
    acq_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    satellite VARCHAR(32) NOT NULL,
    instrument VARCHAR(32) NOT NULL,
    confidence VARCHAR(32) NOT NULL,
    version VARCHAR(32) DEFAULT 'NRT',
    bright_t31 DOUBLE PRECISION,
    frp DOUBLE PRECISION NOT NULL,
    daynight VARCHAR(8),
    raw_hash VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_observations_point ON observations USING GIST (point_geom);
CREATE INDEX IF NOT EXISTS idx_observations_acq_datetime ON observations (acq_datetime);
CREATE INDEX IF NOT EXISTS idx_observations_hash ON observations (raw_hash);

-- 4. Alerts & Actionable Dispatch Table
CREATE TABLE IF NOT EXISTS alerts (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) REFERENCES events(id) ON DELETE CASCADE,
    facility_id VARCHAR(64) REFERENCES facilities(id),
    level VARCHAR(32) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'DISPATCHED',
    message TEXT NOT NULL,
    operational_action TEXT NOT NULL,
    recipient_role VARCHAR(64) NOT NULL,
    channels VARCHAR(128) NOT NULL,
    cooldown_until TIMESTAMP WITH TIME ZONE,
    acknowledged_by VARCHAR(64),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Human-in-the-Loop Analyst Feedback Table
CREATE TABLE IF NOT EXISTS analyst_feedback (
    id VARCHAR(64) PRIMARY KEY,
    event_id VARCHAR(64) REFERENCES events(id) ON DELETE CASCADE,
    analyst_id VARCHAR(64) NOT NULL,
    verified_class VARCHAR(64) NOT NULL,
    verified_state VARCHAR(64) NOT NULL,
    comment TEXT,
    evidence_urls TEXT,
    confidence_rating INTEGER CHECK (confidence_rating BETWEEN 1 AND 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tamper-Evident Audit Log Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(64) PRIMARY KEY,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,
    actor_id VARCHAR(64) NOT NULL,
    payload_json TEXT NOT NULL,
    sha256_checksum VARCHAR(64) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. High-Performance Spatial Query Function: Nearest Facility Within Buffer
CREATE OR REPLACE FUNCTION get_nearest_facility(
    p_lat DOUBLE PRECISION,
    p_lon DOUBLE PRECISION,
    p_max_distance_meters DOUBLE PRECISION DEFAULT 5000.0
)
RETURNS TABLE (
    facility_id VARCHAR(64),
    facility_name VARCHAR(255),
    distance_meters DOUBLE PRECISION,
    is_inside BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.name,
        ST_Distance(f.centroid_geom::geography, ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography) AS distance_meters,
        CASE 
            WHEN f.polygon_geom IS NOT NULL THEN ST_Contains(f.polygon_geom, ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326))
            ELSE FALSE
        END AS is_inside
    FROM facilities f
    WHERE ST_DWithin(f.centroid_geom::geography, ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326)::geography, p_max_distance_meters)
    ORDER BY distance_meters ASC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

