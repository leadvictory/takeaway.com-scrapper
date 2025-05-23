import re
import json
import csv
import os
import requests

def save_menu(menu_name):
        
    os.makedirs("images", exist_ok=True)
    source_name = menu_name + ".html"

    with open(source_name, "r", encoding="utf-8") as f:
        html = f.read()

    match_items = re.search(r'"items"\s*:\s*({)', html)
    if not match_items:
        print("❌ 'items' block not found.")
        exit()

    start_index = match_items.start(1)
    decoder = json.JSONDecoder()

    try:
        parsed_obj, _ = decoder.raw_decode(html[start_index:])
        print(f"✅ Extracted {len(parsed_obj)} menu items.")

        match_categories = re.search(r'"categories"\s*:\s*(\[\{.*?\}])\s*,', html, re.DOTALL)
        if not match_categories:
            print("❌ 'categories' block not found.")
            exit()

        categories = json.loads(match_categories.group(1))

        item_to_category = {}
        for cat in categories:
            for item_id in cat.get("itemIds", []):
                item_to_category[str(item_id)] = cat.get("name", "")

        filename = f"menu_{menu_name}.csv"
        with open(filename, "w", newline='', encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)
            # writer.writerow([
            #     "id", "id2", "-", "-", "-", "-", "name", "-", "description", "price", "price2",
            #     "-", "-", "-", "option groups", "-", "-", "-", "-", "photo", "-", "-", "-", "category", "-"
            # ])

            for idx, (item_id, item) in enumerate(parsed_obj.items(), start=1):
                name = item.get("name", "").strip()
                desc = item.get("description", "").strip()

                variations = item.get("variations", [])
                if variations:
                    base_price = variations[0].get("basePrice", "")
                    modifiers = variations[0].get("modifierGroupsIds", [])
                else:
                    base_price = ""
                    modifiers = []

                modifier_str = ",".join(modifiers)

                image_name = ""
                if item.get("imageSources"):
                    image_path = item["imageSources"][0].get("path", "")
                    if image_path:
                        image_id = image_path.split("/")[-1]
                        image_name = f"{image_id}.webp"
                        transformed_url = (
                            f"https://just-eat-prod-eu-res.cloudinary.com/image/upload/"
                            f"c_fill,q_auto,ar_1:1,c_thumb,h_120,w_120/f_auto/q_auto/v1/nl/dishes/brg_anne_max/{image_id}"
                        )
                        image_file_path = os.path.join("images", image_name)
                        try:
                            response = requests.get(transformed_url, timeout=10)
                            if response.status_code == 200:
                                with open(image_file_path, "wb") as img_file:
                                    img_file.write(response.content)
                            else:
                                print(f"⚠️  Image not found: {transformed_url}")
                        except Exception as e:
                            print(f"❌ Failed to download {image_name}: {e}")

                category_name = item_to_category.get(item_id, "")

                writer.writerow([
                    idx, idx, "", "", "", "", name, "", desc,
                    base_price, base_price, "0", "0", "0",
                    modifier_str, "0", "0", "delivery,takeaway", "1",
                    image_name, "", "", "9", category_name, ""
                ])

        print("💾 Saved to menu.csv")

    except json.JSONDecodeError as e:
        print("❌ Failed to parse items JSON:", e)
