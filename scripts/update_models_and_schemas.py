with open("backend/app/db/models.py", "r", encoding="utf-8") as f:
    code = f.read()

target = '    source_class = Column(String(32), default="UNCERTAIN")'
replacement = """    source_class = Column(String(32), default="UNCERTAIN")
    abnormality_state = Column(String(32), default="NORMAL")  # NORMAL, ELEVATED, ABNORMAL_EXCURSION, ESCALATING, CRITICAL_FIRE
    abnormality_score = Column(Float, default=0.0)  # 0.0 to 1.0 continuous severity
    conformal_set_json = Column(Text, nullable=True)  # JSON list of classes in conformal set"""

if target in code and "abnormality_state" not in code:
    code = code.replace(target, replacement)
    with open("backend/app/db/models.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Updated backend/app/db/models.py with abnormality fields.")
else:
    print("models.py already has abnormality fields or target not found.")

# Update schemas/event.py
with open("backend/app/schemas/event.py", "r", encoding="utf-8") as f:
    schema_code = f.read()

s_target = "    source_class: str"
s_replacement = """    source_class: str
    abnormality_state: str = "NORMAL"
    abnormality_score: float = 0.0"""

if s_target in schema_code and "abnormality_state" not in schema_code:
    schema_code = schema_code.replace(s_target, s_replacement)

if "conformal_prediction_set" not in schema_code:
    detail_target = "    shap_explanation: Optional[Dict[str, Any]] = None"
    detail_replacement = """    shap_explanation: Optional[Dict[str, Any]] = None
    conformal_prediction_set: Optional[List[str]] = None"""
    schema_code = schema_code.replace(detail_target, detail_replacement)

with open("backend/app/schemas/event.py", "w", encoding="utf-8") as f:
    f.write(schema_code)
print("Updated backend/app/schemas/event.py with abnormality and conformal fields.")
