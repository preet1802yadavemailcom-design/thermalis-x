with open("backend/app/services/conformal_prediction.py", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace('"""\n    Inductive', 'r"""\n    Inductive')
c = c.replace('"""\n        Compute nonconformity', 'r"""\n        Compute nonconformity')
c = c.replace('"""\n        Construct conformal', 'r"""\n        Construct conformal')
with open("backend/app/services/conformal_prediction.py", "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed conformal_prediction.py raw docstrings.")
