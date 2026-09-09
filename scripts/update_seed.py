with open("scripts/seed_database.py", "r", encoding="utf-8") as f:
    code = f.read()

# Update seed definitions
code = code.replace(
    'source_class="IND_ACCIDENT",',
    'source_class="IND_ACCIDENT",\n        abnormality_state="CRITICAL_FIRE",\n        abnormality_score=0.95,\n        conformal_set_json=json.dumps(["IND_ACCIDENT"]),'
)

code = code.replace(
    'source_class="MINE_HEAT",',
    'source_class="MINE_HEAT",\n        abnormality_state="NORMAL",\n        abnormality_score=0.05,\n        conformal_set_json=json.dumps(["MINE_HEAT"]),'
)

code = code.replace(
    'source_class="AGRI_BURN",',
    'source_class="AGRI_BURN",\n        abnormality_state="NORMAL",\n        abnormality_score=0.05,\n        conformal_set_json=json.dumps(["AGRI_BURN"]),'
)

code = code.replace(
    'source_class="GAS_FLARE",',
    'source_class="GAS_FLARE",\n        abnormality_state="NORMAL",\n        abnormality_score=0.05,\n        conformal_set_json=json.dumps(["GAS_FLARE"]),'
)

code = code.replace(
    'source_class="IND_NORMAL",',
    'source_class="IND_NORMAL",\n        abnormality_state="NORMAL",\n        abnormality_score=0.05,\n        conformal_set_json=json.dumps(["IND_NORMAL"]),'
)

with open("scripts/seed_database.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated scripts/seed_database.py with abnormality and conformal fields.")
