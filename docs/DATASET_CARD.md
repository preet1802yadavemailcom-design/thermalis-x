# THERMALIS-X Dataset Card (Gebru et al. Guidelines)

## 1. Dataset Summary
The THERMALIS-X benchmark dataset consists of 2,000 spatiotemporally clustered thermal events spanning 10 distinct classes across Indian industrial, mining, and agricultural regions.

## 2. Class Distribution
- `IND_ACCIDENT`: 200 events (catastrophic industrial fires with baseline excursions).
- `IND_NORMAL`: 200 events (routine furnace and operational heat within P10-P90 envelope).
- `GAS_FLARE`: 200 events (refinery/petrochemical flaring point sources).
- `WILDFIRE`: 200 events (vegetative fires in forest/shrub terrain).
- `AGRI_BURN`: 200 events (seasonal cropland residue burning).
- `MINE_HEAT`: 200 events (coal seam and overburden smoldering).
- `POWER_HEAT`: 200 events (continuous thermal power plant emissions).
- `OTHER_NATURAL`: 200 events (geothermal and solar thermal bare rock inertia).
- `FALSE_POSITIVE`: 200 events (solar glint and cloud edge artifacts).
- `UNCERTAIN`: 200 events (ambiguous multi-sensor observations triggering abstention).

## 3. Zero Circular Labeling & Isolation Protocol
Labels are anchored on independent ground truth:
- Industrial accidents are defined by documented disaster manifests, off-stack expansion, and baseline violations.
- Routine operational heat and gas flares are anchored on verified facility operational permits and continuous long-term thermal baselines.
- Evaluation partitions strictly isolate entire industrial facilities (Facility-Held-Out GroupKFold) to guarantee the model learns thermal physics rather than facility coordinates.
