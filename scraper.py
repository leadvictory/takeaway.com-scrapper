import sys
from save import save_html
from menu import save_menu
from menu_config import save_menu_config
from options_config import save_option_config
from options import save_options

if len(sys.argv) < 2:
    print("No URL provided.")
    sys.exit(1)

URL = sys.argv[1].strip()
print(URL)
menu = save_html(URL)

save_menu_config(menu)
save_option_config(menu)
save_options(menu)
save_menu(menu)
