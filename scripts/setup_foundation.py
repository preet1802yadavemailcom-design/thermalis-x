import os

env_content = """# THERMALIS-X Environment Configuration
APP_NAME=THERMALIS-X
APP_ENV=development
DEBUG=false
SECRET_KEY=thermalis-dev-secret-key-change-in-production-sha256-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Database Configuration (PostGIS / SQLite Fallback)
DATABASE_URL=sqlite:///./thermalis.db

# NASA FIRMS API
FIRMS_BASE_URL=https://firms.modaps.eosdis.nasa.gov/api
FIRMS_MAP_KEY=SAMPLE_FIRMS_MAP_KEY
FIRMS_CACHE_TTL_SECONDS=3600

# Open-Meteo Weather API
WEATHER_BASE_URL=https://api.open-meteo.com/v1

# Element84 STAC Satellite API (Sentinel-2 L2A)
STAC_API_URL=https://earth-search.aws.element84.com/v1

# OSM Overpass API
OVERPASS_URL=https://overpass-api.de/api/interpreter

# System Operational Parameters
SPATIAL_CLUSTER_RADIUS_KM=1.25
TEMPORAL_WINDOW_HOURS=24.0
BASELINE_WINDOW_DAYS=180
ALERT_COOLDOWN_MINUTES=60
UNCERTAINTY_THRESHOLD_ENTROPY=0.60
UNCERTAINTY_THRESHOLD_MARGIN=0.15

# Operational Modes
DEMO_MODE=true
REAL_DATA_MODE=false
"""

with open(".env.example", "w", encoding="utf-8") as f:
    f.write(env_content)

with open(".env", "w", encoding="utf-8") as f:
    f.write(env_content)

pyproject = """[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "thermalis-x"
version = "1.0.0"
description = "AI-Based Detection and Classification of Industrial Fires and Persistent Thermal Sources Using NASA FIRMS, OSM and Satellite Data"
readme = "README.md"
requires-python = ">=3.11"
authors = [{ name = "THERMALIS-X Team", email = "team@thermalis-x.internal" }]
license = { text = "Apache-2.0" }

[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"
"""

with open("pyproject.toml", "w", encoding="utf-8") as f:
    f.write(pyproject)

license_text = """                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   Copyright 2026 THERMALIS-X Contributors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

with open("LICENSE", "w", encoding="utf-8") as f:
    f.write(license_text)

print("Foundation files successfully written.")
