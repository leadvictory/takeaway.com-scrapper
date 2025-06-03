from seleniumbase import SB
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import os

def save_html(URL):
    parsed_url = urlparse(URL)
    menu_name = os.path.basename(parsed_url.path)

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{menu_name}.html"
    filepath = os.path.join(output_dir, filename)
    CHROME_PATH = os.environ.get("CHROME_PATH", "/usr/bin/google-chrome")

    with SB(uc=True, headless=True, binary_location=CHROME_PATH) as sb:
    # with SB(uc=True, headless=True) as sb:
        sb.maximize_window()
        sb.timeout = 1
        sb.uc_open_with_reconnect(URL, reconnect_time=12)
        sb.sleep(3)

        html = sb.get_page_source()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        print(f" Page source saved to {filepath}")

    return menu_name
