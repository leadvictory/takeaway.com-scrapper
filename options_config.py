import re
import json
import csv

# ---------- helper to convert 0-based index → a, b, …, z, aa, ab, … ----------
def index_to_letters(idx: int) -> str:
    """0 → a, 1 → b … 25 → z, 26 → aa, 27 → ab, … (lower-case)."""
    letters = []
    while True:
        idx, rem = divmod(idx, 26)
        letters.append(chr(ord('a') + rem))
        if idx == 0:
            break
        idx -= 1          # Excel-style carry
    return ''.join(reversed(letters))
# -----------------------------------------------------------------------------


# ---------- read HTML --------------------------------------------------------
with open("annemax_menu.html", "r", encoding="utf-8") as fh:
    html = fh.read()

m = re.search(r'"modifierSets"\s*:\s*(\[\{.*?}])', html, re.DOTALL)
if not m:
    print("❌ Could not find 'modifierSets' block.")
    raise SystemExit

raw_json = m.group(1)

# ---------- parse JSON -------------------------------------------------------
try:
    modifier_sets = json.loads(raw_json)
except json.JSONDecodeError as e:
    print("❌ JSON parsing failed:", e)
    raise SystemExit

print(f"✅ Found {len(modifier_sets)} modifier sets.")

# ---------- write CSV --------------------------------------------------------
with open("options_config.csv", "w", newline='', encoding="utf-8-sig") as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["group id", "group type", "title"])

    for i, item in enumerate(modifier_sets):
        mod = item.get("modifier", {})
        group_id      = index_to_letters(i)                  # a, b, …, aa, ab …
        max_choices   = mod.get("maxChoices", 1)
        group_type    = 1 if max_choices == 1 else 2         # 1 = mandatory (select), 2 = optional (checkbox)
        title         = mod.get("name", "").strip()

        writer.writerow([group_id, group_type, title])

print("💾 Saved to options_config.csv")
