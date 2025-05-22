import re
import json
import csv

# Load HTML
with open("annemax_menu.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract categories JSON
match = re.search(r'"categories"\s*:\s*(\[\{.*?\}])\s*,', html, re.DOTALL)
if not match:
    print("❌ Could not find 'categories' block.")
    exit()

raw_json = match.group(1)

try:
    categories = json.loads(raw_json)
    print(f"✅ Found {len(categories)} categories.")

    with open("menu_config.csv", "w", newline='', encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Header
        writer.writerow(["id", "category name", "-", "-", "subtitle", "id2", "-"])

        # Data rows
        for idx, cat in enumerate(categories, start=1):
            writer.writerow([
                idx,
                cat.get("name", "").strip(),
                "",
                "",
                cat.get("description", "").strip(),
                idx,
                ""
            ])

    print("💾 Saved as menu_config.csv")

except Exception as e:
    print(f"❌ JSON parsing failed: {e}")
