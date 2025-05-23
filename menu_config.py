import re
import json
import csv

def save_menu_config(menu_name):
    source_name = menu_name + ".html"
    with open(source_name, "r", encoding="utf-8") as f:
        html = f.read()

    match = re.search(r'"categories"\s*:\s*(\[\{.*?\}])\s*,', html, re.DOTALL)
    if not match:
        print("❌ Could not find 'categories' block.")
        exit()

    raw_json = match.group(1)

    try:
        categories = json.loads(raw_json)
        print(f"✅ Found {len(categories)} categories.")
        filename = f"menu_config_{menu_name}.csv"
        with open(filename, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            # writer.writerow(["id", "category name", "-", "-", "subtitle", "id2", "-"])

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

        print(f"💾 Saved as {filename}")

    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")
