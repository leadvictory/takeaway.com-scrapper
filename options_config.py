import re
import json
import csv
import os

def index_to_letters(idx: int) -> str:
    letters = []
    while True:
        idx, rem = divmod(idx, 26)
        letters.append(chr(ord('a') + rem))
        if idx == 0:
            break
        idx -= 1
    return ''.join(reversed(letters))

def save_option_config(menu_name):
    base_dir = "downloads"
    source_name = os.path.join("uploads", f"{menu_name}.html")
    filename = os.path.join(base_dir, f"options_config_{menu_name}.csv")

    try:
        with open(source_name, "r", encoding="utf-8") as fh:
            html = fh.read()
    except FileNotFoundError:
        print(f"File not found: {source_name}")
        return

    m = re.search(r'"modifierGroups"\s*:\s*(\[\{.*?}])', html, re.DOTALL)
    if not m:
        print("No 'modifierGroups' block found in the HTML.")
        modifier_groups = []
    else:
        try:
            modifier_groups = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            print("JSON parsing failed:", e)
            return

    print(f"Found {len(modifier_groups)} modifier groups.")

    name_to_group_id = {}
    group_counter = 0

    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for group in modifier_groups:
            title = group.get("name", "").strip()
            if not title or title in name_to_group_id:
                continue

            max_choices = group.get("maxChoices", 1)
            group_type = 1 if max_choices == 1 else 2

            group_id = index_to_letters(group_counter)
            name_to_group_id[title] = group_id
            group_counter += 1

            writer.writerow([group_id, group_type, title, ""])

    print(f"Saved to {filename}")
