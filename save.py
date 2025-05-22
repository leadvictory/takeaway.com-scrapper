from seleniumbase import SB
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import os

def save_html():
    URL="https://www.thuisbezorgd.nl/menu/annemax-14"
    # URL = input("Enter menu URL: ").strip()

    parsed_url = urlparse(URL)
    menu_name = os.path.basename(parsed_url.path)
    filename = os.path.basename(parsed_url.path) + ".html" 
    with SB(uc=True) as sb:
    # with SB(uc=True, headless=True) as sb:
        sb.maximize_window()
        sb.timeout = 1
        sb.uc_open_with_reconnect(URL, reconnect_time=12)
        sb.sleep(3)

        html = sb.get_page_source()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ Page source saved to {filename}")
    return menu_name
