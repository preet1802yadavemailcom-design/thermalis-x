# THERMALIS-X: Feature Pipeline & Interpretability Report
**Feature Engineering & Model Attribution Architecture**

---

## 1. 48-Dimensional Feature Taxonomical Breakdown

| Feature Category | Count | Key Features | Physical Rationale |
| :--- | :---: | :--- | :--- |
| **Thermal Radiative** | 8 | `max_frp`, `mean_frp`, `total_fre_mj`, `frp_variance`, `frp_p95` | Absolute radiative energy output distinguishes high-heat furnaces and major industrial blazes from minor fires. |
| **Temporal Dynamics** | 8 | `duration_hours`, `observation_count`, `frp_trend`, `revisit_consistency` | Accidental fires surge and decay rapidly; flare stacks and coal seam fires remain persistent over months/years. |
| **Spatial Morphology** | 10 | `area_ha`, `hull_perimeter_km`, `compactness`, `aspect_ratio`, `spread_velocity_kmh` | Point flares maintain near-zero area ($<1\text{ ha}$) and extreme compactness; wildfires and agricultural burns exhibit high elongation and rapid perimeter expansion. |
| **Facility Proximity & Baseline** | 12 | `distance_to_facility_km`, `within_footprint_flag`, `frp_to_median_ratio`, `mad_z_score`, `baseline_excursion_score` | Core discriminatory context: compares current thermal radiance against the facility's 180-day operational baseline. |
| **Atmospheric & Dispersion** | 10 | `wind_speed_kmh`, `wind_direction_deg`, `air_temp_c`, `relative_humidity`, `plume_drift_km` | Evaluates smoke dispersion heading and potential threat to neighboring residential populations. |

---

## 2. SHAP Global Feature Importance Ranking

1. `mad_z_score` (Mean |SHAP| = 0.384): Strongest discriminator between routine flaring and industrial fires.
2. `distance_to_facility_km` (Mean |SHAP| = 0.291): Differentiates industrial site fires from off-site wildfires/agricultural burns.
3. `duration_hours` (Mean |SHAP| = 0.245): Identifies multi-week coal seam fires versus short-lived agricultural clearing.
4. `compactness` (Mean |SHAP| = 0.210): Isolates localized flare stacks from expanding fire fronts.
5. `max_frp` (Mean |SHAP| = 0.188): Energy ceiling metric.
