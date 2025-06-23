import re
import json
import csv
import os

def index_to_letters(index):
    result = ""
    while True:
        index, rem = divmod(index, 26)
        result = chr(97 + rem) + result
        if index == 0:
            break
        index -= 1
    return result

def save_options(menu_name):
    base_dir = "downloads"
    source_name = os.path.join("uploads", f"{menu_name}.html")
    config_name = os.path.join(base_dir, f"options_config_{menu_name}.csv")
    output_name = os.path.join(base_dir, f"options_{menu_name}.csv")

    group_id_map = {}

    try:
        with open(config_name, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=["group id", "group type", "title"])
            for row in reader:
                name = row["title"].strip()
                group_id = row["group id"]
                group_id_map[name] = group_id
    except FileNotFoundError:
        print(f"Config file not found: {config_name}")
        return

    try:
        with open(source_name, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print(f"Source HTML file not found: {source_name}")
        return

    match_groups = re.search(r'"modifierGroups"\s*:\s*(\[\{.*?\}])', html, re.DOTALL)
    if not match_groups:
        print("No 'modifierGroups' block found.")
        return

    try:
        modifier_groups = json.loads(match_groups.group(1))
    except json.JSONDecodeError:
        print("Failed to parse modifierGroups JSON.")
        return

    if not modifier_groups:
        print("'modifierGroups' is empty.")
        return

    match_sets = re.search(r'"modifierSets"\s*:\s*(\[\{.*?\}])', html, re.DOTALL)
    if not match_sets:
        print("No 'modifierSets' block found.")
        return

    try:
        modifier_sets = json.loads(match_sets.group(1))
    except json.JSONDecodeError:
        print("Failed to parse modifierSets JSON.")
        return

    if not modifier_sets:
        print("'modifierSets' is empty.")
        return

    modifier_lookup = {str(m["id"]): m["modifier"] for m in modifier_sets if "modifier" in m}
    modifier_id_to_group_name = {}
    for group in modifier_groups:
        group_name = group.get("name", "").strip()
        for mod_id in group.get("modifiers", []):
            modifier_id_to_group_name[str(mod_id)] = group_name

    seen_names = set()
    written = 0

    with open(output_name, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)

        option_id = 1
        for mod_id, mod_data in modifier_lookup.items():
            name = mod_data.get("name", "").strip()
            if not name or name in seen_names:
                continue
            seen_names.add(name)

            group_name = modifier_id_to_group_name.get(mod_id)
            if not group_name:
                continue
            group_id = group_id_map.get(group_name)
            if not group_id:
                continue

            price = mod_data.get("additionPrice", 0)

            writer.writerow([
                group_id,
                option_id,
                option_id,
                "",
                "",
                name,
                "",
                price,
                price,
                price,
                "0",
                "0",
                "0",
                "0",
                "delivery,takeaway",
                "1",
                "9"
            ])
            option_id += 1
            written += 1

    if written == 0:
        print("No valid options were saved.")
    else:
        print(f"Saved {written} unique options to {output_name}")
