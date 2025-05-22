import re
import json
import csv

def index_to_letters(index):
    result = ""
    while True:
        index, rem = divmod(index, 26)
        result = chr(97 + rem) + result
        if index == 0:
            break
        index -= 1
    return result

# Load group ids from options_config.csv
group_id_map = {}
with open("options_config.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["title"].strip()
        group_id = row["group id"]
        group_id_map[name] = group_id

# Load HTML and extract JSON blocks
with open("annemax_menu.html", "r", encoding="utf-8") as f:
    html = f.read()

match_groups = re.search(r'"modifierGroups"\s*:\s*(\[\{.*?\}])', html, re.DOTALL)
if not match_groups:
    print("❌ Could not find 'modifierGroups' block.")
    exit()
modifier_groups_raw = match_groups.group(1)

match_sets = re.search(r'"modifierSets"\s*:\s*(\[\{.*?\}])', html, re.DOTALL)
if not match_sets:
    print("❌ Could not find 'modifierSets' block.")
    exit()
modifier_sets_raw = match_sets.group(1)

try:
    modifier_groups = json.loads(modifier_groups_raw)
    modifier_sets = json.loads(modifier_sets_raw)

    modifier_lookup = {
        str(mod["id"]): mod["modifier"]
        for mod in modifier_sets
    }

    with open("options.csv", "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["group id", "id", "id2", "-", "-", "name", "-", "price", "price2", "0", "1"])

        option_id = 1
        for group in modifier_groups:
            name = group.get("name", "").strip()
            group_letter = group_id_map.get(name)
            if not group_letter:
                continue  # Skip if not found in config

            price = 0
            for mod_id in group.get("modifiers", []):
                mod_data = modifier_lookup.get(str(mod_id))
                if not mod_data:
                    continue
                price += mod_data.get("additionPrice", 0)

            writer.writerow([
                group_letter,
                option_id,
                option_id,
                "",
                "",
                name,
                "",
                price,
                price,
                "0",
                "1"
            ])
            option_id += 1

    print(f"💾 Saved {option_id - 1} options to options.csv")

except Exception as e:
    print("❌ JSON parsing failed:", e)
