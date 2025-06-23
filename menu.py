import re
import json
import csv
import os
import requests
import shutil

def save_menu(menu_name):
    base_dir = "downloads"
    os.makedirs(base_dir, exist_ok=True)

    source_name = os.path.join("uploads", f"{menu_name}.html")
    option_config_name = os.path.join(base_dir, f"options_config_{menu_name}.csv")
    output_csv = os.path.join(base_dir, f"menu_{menu_name}.csv")
    image_folder = os.path.join(base_dir, f"images_{menu_name}")
    os.makedirs(image_folder, exist_ok=True)

    option_map = {}
    if os.path.exists(option_config_name):
        with open(option_config_name, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=["group id", "group type", "title"])
            for row in reader:
                option_map[row["title"].strip()] = row["group id"].strip()
    else:
        print(f"Option config file not found: {option_config_name}. Continuing with empty option map.")

    try:
        with open(source_name, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print(f"Source file not found: {source_name}")
        return

    match_items = re.search(r'"items"\s*:\s*({)', html)
    if not match_items:
        print("'items' block not found.")
        return

    start_index = match_items.start(1)
    decoder = json.JSONDecoder()
    try:
        parsed_obj, _ = decoder.raw_decode(html[start_index:])
    except json.JSONDecodeError as e:
        print("Failed to parse items JSON:", e)
        return

    print(f"Extracted {len(parsed_obj)} menu items.")

    # Categories
    item_to_category = {}
    match_categories = re.search(r'"categories"\s*:\s*(\[\{.*?\}])\s*,', html, re.DOTALL)
    if match_categories:
        try:
            categories = json.loads(match_categories.group(1))
            for cat in categories:
                for item_id in cat.get("itemIds", []):
                    item_to_category[str(item_id)] = cat.get("name", "")
        except json.JSONDecodeError:
            print("Could not parse 'categories'. Skipping category assignment.")
    else:
        print("'categories' block not found.")

    # Modifier Groups
    modifier_groups = []
    match_modifiers = re.search(r'"modifierGroups"\s*:\s*(\[\{.*?}])', html, re.DOTALL)
    if match_modifiers:
        try:
            modifier_groups = json.loads(match_modifiers.group(1))
        except json.JSONDecodeError:
            print("Could not parse 'modifierGroups'. Continuing without modifiers.")
    else:
        print("'modifierGroups' block not found.")

    with open(output_csv, "w", newline='', encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)

        for idx, (item_id, item) in enumerate(parsed_obj.items(), start=1):
            name = item.get("name", "").strip()
            desc = (item.get("description") or "").strip()

            variations = item.get("variations", [])
            base_price = variations[0].get("basePrice", "") if variations else ""
            modifiers = variations[0].get("modifierGroupsIds", []) if variations else []

            group_ids = []
            for mod_id in modifiers:
                group = next((g for g in modifier_groups if g.get("id") == mod_id), None)
                if group:
                    group_name = group.get("name", "").strip()
                    mapped_id = option_map.get(group_name)
                    if mapped_id:
                        group_ids.append(mapped_id)

            modifier_str = ",".join(group_ids)

            image_name = ""
            if item.get("imageSources"):
                image_path = item["imageSources"][0].get("path", "")
                if image_path:
                    image_id = image_path.split("/")[-1].rsplit(".", 1)[0]
                    image_name = f"{image_id}.png"

                    transformed_part = "c_fill,q_auto,ar_1:1,c_thumb,h_280,w_280/f_png,q_auto"
                    transformed_url = re.sub(
                        r"image/upload/[^/]+/",
                        f"image/upload/{transformed_part}/",
                        image_path
                    )
                    image_file_path = os.path.join(image_folder, image_name)
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
                idx, idx, "", "", "", "", name, "", desc,
                base_price, base_price, "0", "0", "0",
                modifier_str, "0", "0", "delivery,takeaway", "1",
                image_name, "", "", "9", category_name, ""
            ])

    print(f"Saved to {output_csv}")

    zip_path = os.path.join(base_dir, f"images_{menu_name}.zip")
    if os.path.exists(image_folder):
        shutil.make_archive(zip_path[:-4], 'zip', image_folder)
        print(f"Zipped image folder as {zip_path}")
    else:
        print("No image folder to zip.")
