from seleniumbase import SB
from selenium.webdriver.common.by import By

LOGIN_URL = "https://www.thuisbezorgd.nl/menu/annemax-14"

with SB(uc=True) as sb:
    sb.maximize_window()
    sb.timeout = 1
    sb.uc_open_with_reconnect(LOGIN_URL, reconnect_time=12)
    sb.sleep(3)

    # Get and save the page source
    html = sb.get_page_source()
    with open("annemax_menu.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ Page source saved to annemax_menu.html")