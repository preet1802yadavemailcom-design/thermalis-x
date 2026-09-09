# THERMALIS-X Verified External Data Sources & Provenance

| Data Asset | Provider / Organization | Verified Endpoint / URL | Cadence / Update | License | Operational Role in THERMALIS-X |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NASA FIRMS VIIRS** | NASA EOSDIS / NOAA | `https://firms.modaps.eosdis.nasa.gov/api` | Near Real-Time (~3 hrs) | Open Access (Public Domain) | Primary high-resolution ($375\text{m}$) thermal anomaly and FRP stream. |
| **NASA FIRMS MODIS** | NASA EOSDIS (Terra/Aqua) | `https://firms.modaps.eosdis.nasa.gov/api` | Near Real-Time (~3 hrs) | Open Access (Public Domain) | Multi-pass sensor cross-validation and historical baseline corroboration. |
| **OpenStreetMap (OSM)** | OpenStreetMap Foundation | `https://overpass-api.de/api/interpreter` | Continuous updates | ODbL 1.0 | Industrial landuse boundaries, manufacturing tags, and infrastructure footprints. |
| **Global Energy Monitor (GEM)** | Global Energy Monitor | Open Data Catalogs (Coal, Gas, Steel) | Quarterly updates | CC-BY 4.0 | Exact coordinates of power plants, oil refineries, and steel works across India. |
| **Element84 STAC (Sentinel-2)** | ESA Copernicus via Element84 | `https://earth-search.aws.element84.com/v1` | 5-day constellation revisit | Open Copernicus Data Policy | High-resolution ($10\text{m}/20\text{m}$) optical, NIR, and SWIR spectral verification. |
| **Open-Meteo Weather API** | Open-Meteo GmbH | `https://api.open-meteo.com/v1/forecast` | Hourly NRT updates | CC-BY 4.0 | Surface wind speed, direction, ambient temperature, and humidity for smoke drift vectors. |
