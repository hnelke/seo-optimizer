import os

path = r"g:\Meine Ablage\KI-Agenten\SEO-Optimizer\static\app.js"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "historysortselect" in line.lower() or "score_desc" in line.lower():
        print(f"{idx+1}: {line.strip()}")
