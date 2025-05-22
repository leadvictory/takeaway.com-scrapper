import re
import json
import csv

def index_to_letters(idx: int) -> str:
    """0 → a, 1 → b … 25 → z, 26 → aa, 27 → ab, … (lower-case)."""
    letters = []
    while True:
        idx, rem = divmod(idx, 26)
        letters.append(chr(ord('a') + rem))
        if idx == 0:
            break
        idx -= 1
    return ''.join(reversed(letters))

with open("annemax_menu.html", "r", encoding="utf-8") as fh:
    html = fh.read()

# Updated regex to find "modifierGroups"
m = re.search(r'"modifierGroups"\s*:\s*(\[\{.*?}])', html, re.DOTALL)
if not m:
    print("❌ Could not find 'modifierGroups' block.")
    raise SystemExit

raw_json = m.group(1)

try:
    modifier_groups = json.loads(raw_json)
except json.JSONDecodeError as e:
    print("❌ JSON parsing failed:", e)
    raise SystemExit

print(f"✅ Found {len(modifier_groups)} modifier groups.")

name_to_group_id = {}
group_counter = 0

with open("options_config.csv", "w", newline='', encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["group id", "group type", "title"])

    for group in modifier_groups:
        title = group.get("name", "").strip()
        if not title or title in name_to_group_id:
            continue  # Skip duplicates or empty titles

        max_choices = group.get("maxChoices", 1)
        group_type = 1 if max_choices == 1 else 2

        group_id = index_to_letters(group_counter)
        name_to_group_id[title] = group_id
        group_counter += 1

        writer.writerow([group_id, group_type, title])

print("💾 Saved to options_config.csv")
