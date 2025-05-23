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

def save_options(menu_name):
    source_name = menu_name + ".html"
    config_name = f"options_config_{menu_name}.csv"
    group_id_map = {}
    with open(config_name, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["title"].strip()
            group_id = row["group id"]
            group_id_map[name] = group_id

    with open(source_name, "r", encoding="utf-8") as f:
        html = f.read()

    match_groups = re.search(r'"modifierGroups"\s*:\s*(\[\{.*?\}])', html, re.DOTALL)
    if not match_groups:
        print("❌ Could not find 'modifierGroups' block.")
        exit()
    modifier_groups = json.loads(match_groups.group(1))

    match_sets = re.search(r'"modifierSets"\s*:\s*(\[\{.*?\}])', html, re.DOTALL)
    if not match_sets:
        print("❌ Could not find 'modifierSets' block.")
        exit()
    modifier_sets = json.loads(match_sets.group(1))

    modifier_lookup = {str(m["id"]): m["modifier"] for m in modifier_sets}
    modifier_id_to_group_name = {}
    for group in modifier_groups:
        group_name = group.get("name", "").strip()
        for mod_id in group.get("modifiers", []):
            modifier_id_to_group_name[str(mod_id)] = group_name

    seen_names = set()
    filename = f"options_{menu_name}.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        # writer.writerow(["group id", "id", "id2", "-", "-", "name", "-", "price", "price2","-", "-", "-", "-", "-", "-",  "-", "-"])

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

    print(f"💾 Saved {option_id - 1} unique options to {filename}")
