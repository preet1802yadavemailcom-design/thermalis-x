with open("backend/app/services/facility_service.py", "r", encoding="utf-8") as f:
    code = f.read()

shapely_inside = """    def is_inside_facility(self, lat: float, lon: float, facility: Dict[str, Any]) -> bool:
        if not facility.get("footprint_geojson"):
            return False
        try:
            from shapely.geometry import shape, Point
            geom = json.loads(facility["footprint_geojson"])
            poly = shape(geom)
            pt = Point(lon, lat)
            return bool(poly.contains(pt) or poly.touches(pt))
        except Exception:
            return False
"""

# Replace the method in facility_service.py
start_marker = "    def is_inside_facility(self, lat: float, lon: float, facility: Dict[str, Any]) -> bool:"
idx = code.find(start_marker)
if idx != -1:
    code_before = code[:idx]
    code = code_before + shapely_inside

with open("backend/app/services/facility_service.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated FacilityService.is_inside_facility to use Shapely geometry.")
