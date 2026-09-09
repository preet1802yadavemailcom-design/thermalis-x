import glob

# Replace from_orm with model_validate in api endpoints
for path in glob.glob("backend/app/api/v1/*.py"):
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    c = c.replace(".from_orm(", ".model_validate(")
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

print("Updated API endpoints to Pydantic v2 model_validate.")
