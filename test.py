import re, json, csv, os, sys, shutil, requests
from urllib.parse import urlparse

# menu = 'koftecii'
menu = 'annemax-14'
# menu = "oh-my-grill"
# menu = "Anne"
# if len(sys.argv) < 2:
#     print("No HTML file path provided.")
#     sys.exit(1)

# file_path = sys.argv[1].strip()
# menu = os.path.splitext(os.path.basename(file_path))[0]
# output_dir = "downloads"
# menu_url = "https://www.thuisbezorgd.nl/menu/annemax-14"
menu_url = "https://www.thuisbezorgd.nl/menu/de-la-roma"
# fetch_and_save_json(url)
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

def fetch_and_save_json(url, output_file="itemDetails.json"):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.thuisbezorgd.nl/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
        "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(
            f"Request failed: {response.status_code} - {response.text}"
        )

    data = response.json()

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return data

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_categories(manifest_path, output_path="categories.json"):
    manifest = load_json(manifest_path)

    categories = []
    for menu in manifest.get("Menus", []):
        categories.extend(menu.get("Categories", []))

    save_json(categories, output_path)


# ---------- 2. items.json → items_clean.json ----------

def clean_items(items_path, output_path="items_clean.json"):
    with open(items_path, "r", encoding="utf-8") as f:
        items_data = json.load(f)

    cleaned_items = items_data.get("Items", [])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_items, f, indent=4, ensure_ascii=False)


# ---------- 3. itemDetails.json → modifierGroups + modifierSets ----------

def extract_modifiers(item_details_path,
                      groups_out="modifierGroups.json",
                      sets_out="modifierSets.json"):
    data = load_json(item_details_path)

    modifier_groups = data.get("ModifierGroups", [])
    modifier_sets = data.get("ModifierSets", [])

    save_json(modifier_groups, groups_out)
    save_json(modifier_sets, sets_out)

def index_to_letters(idx: int) -> str:
    letters = []
    while True:
        idx, rem = divmod(idx, 26)
        letters.append(chr(ord('a') + rem))
        if idx == 0:
            break
        idx -= 1
    return ''.join(reversed(letters))

def extract_json_array_block(text, key):
    key_pos = text.find(f'"{key}"')
    if key_pos == -1:
        return None

    array_start = text.find('[', key_pos)
    if array_start == -1:
        return None

    bracket_count = 0
    for i in range(array_start, len(text)):
        if text[i] == '[':
            bracket_count += 1
        elif text[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                return text[array_start:i+1]
    return None

def save_all(menu_url):
    menu_name = extract_menu_from_url(menu_url)
    base_dir = "downloads"
    os.makedirs(base_dir, exist_ok=True)
    source_name = os.path.join("uploads", f"{menu_name}.html")
    category_csv = os.path.join(base_dir, f"menu_config_{menu_name}.csv")
    config_name = os.path.join(base_dir, f"options_config_{menu_name}.csv")
    options_name = os.path.join(base_dir, f"options_{menu_name}.csv")
    full_menu_csv = os.path.join(base_dir, f"menu_{menu_name}.csv")
    images_folder = os.path.join(base_dir, f"images_{menu_name}")
    os.makedirs(images_folder, exist_ok=True)
    zip_path = os.path.join(base_dir, f"images_{menu_name}.zip")

    urls = generate_thuisbezorgd_cdn_urls(menu_url)

    for name, cdn_url in urls.items():
        filename = f"{name}.json"
        fetch_and_save_json(cdn_url, filename)


    extract_categories("manifest.json")
    clean_items("items.json")
    extract_modifiers("itemDetails.json")

    categories = load_json("categories.json")
    items = load_json("items_clean.json")
    modifier_groups = load_json("modifiergroups.json")
    modifier_sets = load_json("modifierSets.json")

    try:

        with open(category_csv, "w", newline='', encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)

            for idx, cat in enumerate(categories, start=1):
                writer.writerow([
                    idx,
                    cat.get("Name", "").strip(),
                    cat.get("Description", "").strip(),
                    idx,
                    len(cat.get("ItemIds", [])),
                    "", "", ""
                ])

        print(f"Categories CSV saved to: {category_csv}")

    except json.JSONDecodeError as e:
        print("Failed to parse categories JSON:", e)

    modifier_lookup = {str(m["Id"]): m["Modifier"] for m in modifier_sets if "Modifier" in m}
    
    name_to_group_id = {}
    modifier_id_to_group_id = {}
    seen_groups = []
    group_counter = 0
    full_modifiergroup_id_to_groupid = {}  # NEW: map all modifierGroup.id → group_id

    with open(config_name, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for group in modifier_groups:
            group_id_value = group.get("Id")
            title = group.get("Name", "").strip()
            modifiers = group.get("Modifiers", [])
            if not modifiers:
                continue  # Skip empty modifier groups

            modifier_names = []
            for mod_id in modifiers:
                mod = modifier_lookup.get(str(mod_id))
                if mod:
                    modifier_names.append(mod.get("Name", "").strip())
            modifier_names_sorted = sorted(modifier_names)

            # Check if the group is a duplicate
            duplicate_found = False
            for seen in seen_groups:
                if seen["title"] == title and seen["modifier_count"] == len(modifiers) and seen["modifier_names"] == modifier_names_sorted:
                    group_id = seen["group_id"]  # Use the existing group_id
                    duplicate_found = True
                    break

            if not duplicate_found:
                group_id = index_to_letters(group_counter)
                group_counter += 1

                seen_groups.append({
                    "title": title,
                    "modifier_count": len(modifiers),
                    "modifier_names": modifier_names_sorted,
                    "group_id": group_id
                })

                max_choices = group.get("MaxChoices", 1)
                min_choices = group.get("MinChoices", 1)
                group_type = 2 if min_choices == 0 else 1

                writer.writerow([group_id, group_type, title, ""])

            # ✅ Always map the modifierGroupId → group_id
            full_modifiergroup_id_to_groupid[group_id_value] = group_id

            # ✅ Always map modifier IDs → group_id
            for mod_id in modifiers:
                modifier_id_to_group_id[str(mod_id)] = group_id

    print(f"Saved config to {config_name}")

    seen_names = set()
    written = 0
    # print(modifier_id_to_group_id)
    with open(options_name, "w", newline='', encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        option_id = 1

        for mod_id, mod_data in modifier_lookup.items():
            # print(mod_id)
            if mod_id not in modifier_id_to_group_id:
                # print(mod_id)
                continue

            name = mod_data.get("Name", "").strip()
            # if not name or name in seen_names:
            #     continue
            # seen_names.add(name)

            group_id = modifier_id_to_group_id[mod_id]
            price = mod_data.get("AdditionPrice", 0)

            writer.writerow([
                group_id, option_id, option_id, "", "", name, "", price, price, price,
                "0", "0", "0", "0", "delivery,takeaway", "1", "9"
            ])
            option_id += 1
            written += 1

    if written == 0:
        print("No valid options were saved.")
    else:
        print(f"Saved {written} unique options to {options_name}")

    item_to_category = {}
    for cat in categories:
        for item_id in cat.get("ItemIds", []):
            item_to_category[str(item_id)] = cat.get("Name", "")

    with open(full_menu_csv, "w", newline='', encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        # print(full_modifiergroup_id_to_groupid)
        for idx, item in enumerate(items, start=1):
            item_id = item.get("Id")
            name = item.get("Name", "").strip()
            desc = (item.get("Description") or "").strip()
            variations = item.get("Variations", [])
            base_price = variations[0].get("BasePrice", "") if variations else ""
            modifiers = variations[0].get("ModifierGroupsIds", []) if variations else []

            group_ids = []
            for mod_group_id in modifiers:
                group_id = full_modifiergroup_id_to_groupid.get(mod_group_id)
                if group_id:
                    group_ids.append(group_id)
                else:
                    print(f"Group ID not found for modifierGroupId: {mod_group_id}")

            modifier_str = ",".join(group_ids)

            image_name = ""
            if item.get("ImageSources"):
                image_path = item["ImageSources"][0].get("Path", "")
                if image_path:
                    image_id = image_path.split("/")[-1].rsplit(".", 1)[0]
                    image_name = f"{image_id}.png"

                    transformed_part = "c_fill,q_auto,ar_1:1,c_thumb,h_280,w_280/f_png,q_auto"
                    transformed_url = re.sub(
                        r"image/upload/[^/]+/",
                        f"image/upload/{transformed_part}/",
                        image_path
                    )
                    image_file_path = os.path.join(images_folder, image_name)
                    try:
                        response = requests.get(transformed_url, timeout=10)
                        if response.status_code == 200:
                            with open(image_file_path, "wb") as img_file:
                                img_file.write(response.content)
                        else:
                            print(f"Image not found: {transformed_url}")
                    except Exception as e:
                        print(f"Failed to download {image_name}: {e}")

            category_name = item_to_category.get(item_id, "")

            writer.writerow([
                idx, idx, "", "", "", "", name, "", desc, base_price, base_price,
                "0", "0", "0", modifier_str, "0", "0", "delivery,takeaway",
                "1", image_name, "", "", "9", category_name, ""
            ])

    print(f"Saved full menu to {full_menu_csv}")

    if os.path.exists(images_folder):
        shutil.make_archive(zip_path[:-4], 'zip', images_folder)
        print(f"Zipped image folder as {zip_path}")

save_all(menu_url)
