import sys
from save import save_html
from menu import save_menu
from menu_config import save_menu_config
from options_config import save_option_config
from options import save_options
import os

if len(sys.argv) < 2:
    print("No HTML file path provided.")
    sys.exit(1)

file_path = sys.argv[1].strip()
menu = os.path.splitext(os.path.basename(file_path))[0]
output_dir = "downloads"
print(f"{menu}")
print(f"Processing: {file_path}")
save_menu_config(menu)
save_option_config(menu)
save_options(menu)
save_menu(menu)
