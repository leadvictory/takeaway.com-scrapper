import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse
import os

async def save_html(url):
    parsed_url = urlparse(url)
    menu_name = os.path.basename(parsed_url.path) or "index"
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{menu_name}.html")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved: {filepath}")
        await browser.close()

# Run it
asyncio.run(save_html("https://www.thuisbezorgd.nl/menu/annemax-14"))
