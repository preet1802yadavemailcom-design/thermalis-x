# THERMALIS-X Known Remote Sensing & Boundary Limitations

1. **Satellite Orbital Latency**: VIIRS and MODIS are polar-orbiting satellites with a revisit cadence of 4-6 hours over India. True real-time (<60 second) detection requires geostationary sensors (e.g., INSAT-3D), which have coarser spatial resolution (4 km vs 375m).
2. **Monsoon Cloud Attenuation**: Severe tropical cloud cover can absorb mid-infrared radiance, temporarily masking small thermal sources. THERMALIS-X handles this by broadening uncertainty and tasking synthetic aperture radar (SAR) or optical clearing.
3. **Sub-Pixel Thermal Smearing**: High-temperature point sources (e.g. 1000°C flare) bloom across the 375m VIIRS pixel, causing apparent area dilation that must be normalized via compactness metrics.
