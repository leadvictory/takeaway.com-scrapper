import re, json, csv, os, shutil, requests
from urllib.parse import urlparse

# ---------------- CONFIG ----------------

menu = "annemax-14"
menu_url = "https://www.thuisbezorgd.nl/menu/annemax-14"

BASE_DIR = "downloads"
os.makedirs(BASE_DIR, exist_ok=True)

# ---------------- CDN HELPERS ----------------
def extract_menu_from_url(menu_url: str) -> str:
    return urlparse(menu_url).path.rstrip("/").split("/")[-1]

def generate_thuisbezorgd_cdn_urls(menu_url, locale="nl"):
    slug = urlparse(menu_url).path.rstrip("/").split("/")[-1]
    base = "https://globalmenucdn.eu-central-1.production.jet-external.com"
    return {
        "manifest": f"{base}/{slug}_{locale}_manifest.json",
        "items": f"{base}/{slug}_{locale}_items.json",
        "itemDetails": f"{base}/{slug}_{locale}_itemDetails.json",
    }

def fetch_and_save_json(url, output_file):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.thuisbezorgd.nl/",
        "User-Agent": "Mozilla/5.0",
    }
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(r.json(), f, indent=4, ensure_ascii=False)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------------- JSON EXTRACTION ----------------

def extract_categories(manifest_path):
    manifest = load_json(manifest_path)
    categories = []
    for menu in manifest.get("Menus", []):
        categories.extend(menu.get("Categories", []))
    save_json(categories, "categories.json")

def clean_items(items_path):
    items = load_json(items_path).get("Items", [])
    save_json(items, "items_clean.json")

def extract_modifiers(item_details_path):
    data = load_json(item_details_path)
    save_json(data.get("ModifierGroups", []), "modifierGroups.json")
    save_json(data.get("ModifierSets", []), "modifierSets.json")

# ---------------- UTIL ----------------

def index_to_letters(idx):
    s = ""
    while True:
        idx, r = divmod(idx, 26)
        s = chr(ord("a") + r) + s
        if idx == 0:
            return s
        idx -= 1

# ---------------- MAIN PIPELINE ----------------

def save_all(menu_url):
    menu_name = extract_menu_from_url(menu_url)
    urls = generate_thuisbezorgd_cdn_urls(menu_url)
    for name, url in urls.items():
        fetch_and_save_json(url, f"{name}.json")

    extract_categories("manifest.json")
    clean_items("items.json")
    extract_modifiers("itemDetails.json")

    categories = load_json("categories.json")
    items = load_json("items_clean.json")
    modifier_groups = load_json("modifierGroups.json")
    modifier_sets = load_json("modifierSets.json")

    # ---------- CATEGORY CSV ----------
    category_csv = os.path.join(BASE_DIR, f"menu_config_{menu_name}.csv")
    with open(category_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        for i, c in enumerate(categories, 1):
            writer.writerow([
                i,
                c.get("Name", ""),
                c.get("Description", ""),
                i,
                len(c.get("ItemIds", [])),
                "", "", ""
            ])

    # ---------- MODIFIER LOOKUP ----------
    modifier_lookup = {
        str(m["modifier"]["id"]): m["modifier"]
        for m in modifier_sets if "modifier" in m
    }

    # ---------- OPTIONS CONFIG ----------
    config_csv = os.path.join(BASE_DIR, f"options_config_{menu_name}.csv")
    modifier_id_to_group = {}
    group_map = {}
    counter = 0

    with open(config_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for g in modifier_groups:
            mods = g.get("modifiers", [])
            if not mods:
                continue
            gid = index_to_letters(counter)
            counter += 1
            group_map[g["id"]] = gid
            for m in mods:
                modifier_id_to_group[str(m)] = gid
            writer.writerow([gid, 1, g.get("name", ""), ""])

    # ---------- OPTIONS ----------
    options_csv = os.path.join(BASE_DIR, f"options_{menu_name}.csv")
    with open(options_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        oid = 1
        for mid, m in modifier_lookup.items():
            if mid not in modifier_id_to_group:
                continue
            writer.writerow([
                modifier_id_to_group[mid], oid, oid, "", "",
                m.get("name", ""),
                "", m.get("additionPrice", 0),
                m.get("additionPrice", 0),
                m.get("additionPrice", 0),
                "0","0","0","0",
                "delivery,takeaway","1","9"
            ])
            oid += 1

    # ---------- ITEM → CATEGORY MAP ----------
    item_to_category = {}
    for c in categories:
        for iid in c.get("ItemIds", []):
            item_to_category[str(iid)] = c.get("Name", "")

    # ---------- MENU CSV + IMAGES ----------
    images_dir = os.path.join(BASE_DIR, f"images_{menu_name}")
    os.makedirs(images_dir, exist_ok=True)

    menu_csv = os.path.join(BASE_DIR, f"menu_{menu_name}.csv")
    with open(menu_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        for i, item in enumerate(items, 1):
            variations = item.get("Variations", [])
            price = variations[0].get("BasePrice", "") if variations else ""
            mod_ids = variations[0].get("ModifierGroupsIds", []) if variations else []
            mod_groups = ",".join(filter(None, (group_map.get(m) for m in mod_ids)))

            image_name = ""
            if item.get("ImageSources"):
                path = item["ImageSources"][0].get("Path", "")
                if path:
                    image_name = path.split("/")[-1].rsplit(".",1)[0] + ".png"
                    url = re.sub(
                        r"image/upload/[^/]+/",
                        "image/upload/c_fill,q_auto,ar_1:1,c_thumb,h_280,w_280/f_png,q_auto/",
                        path
                    )
                    try:
                        r = requests.get(url, timeout=10)
                        if r.status_code == 200:
                            with open(os.path.join(images_dir, image_name), "wb") as img:
                                img.write(r.content)
                    except:
                        pass

            writer.writerow([
                i, i, "", "", "", "",
                item.get("Name", ""),
                "",
                item.get("Description", ""),
                price, price,
                "0","0","0",
                mod_groups,
                "0","0",
                "delivery,takeaway",
                "1",
                image_name,
                "","",
                "9",
                item_to_category.get(item.get("Id",""), ""),
                ""
            ])

    shutil.make_archive(images_dir, "zip", images_dir)
    print("DONE")

# ---------------- RUN ----------------

save_all(menu_url)
