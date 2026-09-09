with open("backend/app/services/firms_ingestion.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace any multiline split
content = content.replace('lines = resp.text.strip().split("\n', 'lines = resp.text.strip().split("\\n')
content = content.replace('.split("\n")', '.split("\\n")')
# Also handle splitlines() which is cleaner and safer
content = content.replace('lines = resp.text.strip().split("\\n")', 'lines = resp.text.strip().splitlines()')
content = content.replace('lines = resp.text.strip().split("\n")', 'lines = resp.text.strip().splitlines()')

with open("backend/app/services/firms_ingestion.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed firms_ingestion split lines.")
