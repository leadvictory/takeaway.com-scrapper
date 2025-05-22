from save import save_html
from menu import save_menu
from menu_config import save_menu_config
from options_config import save_option_config
from options import save_options

menu = save_html()
save_menu(menu)
save_menu_config(menu)
save_option_config(menu)
save_options(menu)