# THERMALIS-X: Multi-Sensor Remote Sensing & Satellite Architecture
**Technical Reference Document**

---

## 1. Satellite Sensor Hierarchy

| Sensor System | Platform | Spectral Channels | Spatial Resolution | Revisit Cadence | Primary Operational Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VIIRS** | Suomi-NPP, NOAA-20, NOAA-21 | I4 (3.74 μm MWIR), I5 (11.45 μm LWIR) | 375 m at nadir | ~12 hours (day/night) | Core active thermal anomaly detection; FRP quantification |
| **MODIS** | Terra, Aqua | Band 21/22 (3.9 μm), Band 31 (11.0 μm) | 1,000 m | 1–2 days | Secondary active fire cross-validation |
| **MSI** | Sentinel-2A/2B | Band 11 (1.61 μm), Band 12 (2.19 μm SWIR) | 20 m | 5 days | High-resolution sub-pixel hotspot localization & plume verification |
| **OLI / TIRS** | Landsat-8/9 | Band 6/7 (SWIR), Band 10 (10.9 μm TIR) | 30 m (SWIR), 100 m (TIR) | 8 days | Multispectral thermal validation and burn scar extent |
| **Imager** | ISRO INSAT-3D / 3DR | MIR (3.9 μm), TIR-1 (10.8 μm), TIR-2 (12.0 μm) | 4,000 m | **15–30 minutes** | Continuous geostationary surveillance over the Indian landmass |
| **C-SAR** | Sentinel-1A | C-band (5.405 GHz) Synthetic Aperture Radar | 10 m (IW mode) | 6–12 days | All-weather, cloud-penetrating radar backscatter change detection |

---

## 2. Mathematical Sub-Pixel Deconvolution (Dozier Dual-Channel Model)

Given a satellite pixel with observed brightness temperatures $T_4$ in the $3.74\,\mu\text{m}$ (MWIR) band and $T_{11}$ in the $11.45\,\mu\text{m}$ (LWIR) band:

$$L_4(T_4) = p \cdot B_4(T_f) + (1 - p) \cdot B_4(T_b)$$
$$L_{11}(T_{11}) = p \cdot B_{11}(T_f) + (1 - p) \cdot B_{11}(T_b)$$

Where:
- $B_\lambda(T)$ is the Planck blackbody spectral radiance function.
- $T_b$ is the ambient background surface temperature (Kelvin).
- $T_f$ is the true sub-pixel fire/emitter temperature (Kelvin).
- $p$ is the fractional sub-pixel area occupied by the thermal emitter ($0 < p \le 1$).

By numerically inverting this system of non-linear equations, THERMALIS-X estimates both $T_f$ and $p$:
- **Routine Industrial Gas Flare**: $T_f \in [1000\text{ K}, 1800\text{ K}]$, $p \in [10^{-4}, 10^{-2}]$, highly stable across seasons.
- **Accidental Petrochemical Fire**: $T_f \in [600\text{ K}, 950\text{ K}]$, $p$ monotonically increasing over successive satellite revisits ($dp/dt > 0$).
- **Subsurface Coal Fire**: $T_f \in [400\text{ K}, 650\text{ K}]$, $p$ extensive ($>0.1$), spatially stationary over multi-year periods.
