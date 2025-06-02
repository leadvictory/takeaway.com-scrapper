import re
import json
import csv
import os

def save_menu_config(menu_name):
    base_dir = "downloads"
    source_name = os.path.join(base_dir, f"{menu_name}.html")
    output_csv = os.path.join(base_dir, f"menu_config_{menu_name}.csv")

    try:
        with open(source_name, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print(f"Source file not found: {source_name}")
        return

    match = re.search(r'"categories"\s*:\s*(\[\{.*?\}])\s*,', html, re.DOTALL)
    if not match:
        print("Could not find 'categories' block.")
        return

    raw_json = match.group(1)

    try:
        categories = json.loads(raw_json)
        print(f"Found {len(categories)} categories.")

        with open(output_csv, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            for idx, cat in enumerate(categories, start=1):
                writer.writerow([
                    idx,
                    cat.get("name", "").strip(),
                    "",
                    cat.get("description", "").strip(),
                    idx,
                    idx,
                    "",
                    ""
                ])

        print(f"Saved as {output_csv}")

    except Exception as e:
        print(f"JSON parsing failed: {e}")
