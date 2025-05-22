from seleniumbase import SB
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
import os

# Input the URL dynamically
URL = input("Enter menu URL: ").strip()

# Extract the last part of the path for filename
parsed_url = urlparse(URL)
filename = os.path.basename(parsed_url.path) + ".html"  # e.g., annemax-14.html

with SB(uc=True) as sb:
    sb.maximize_window()
    sb.timeout = 1
    sb.uc_open_with_reconnect(URL, reconnect_time=12)
    sb.sleep(3)

    # Save page source to a dynamic file name
    html = sb.get_page_source()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Page source saved to {filename}")
