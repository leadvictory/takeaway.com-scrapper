import cloudscraper

url = "https://www.thuisbezorgd.nl/menu/oh-my-grill"

scraper = cloudscraper.create_scraper(
    browser={
        "browser": "chrome",
        "platform": "windows",
        "mobile": False
    }
)

# cookies = {
#     "cf_clearance": "YOUR_CF_CLEARANCE_HERE",
#     "__cf_bm": "YOUR_BM_COOKIE",
#     "je-auser": "3f13c73b-294a-4b98-b006-c00299f81472",
#     # Add ALL cookies your browser shows
# }

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

response = scraper.get(url, headers=headers)

if response.status_code == 200:
    with open("oh_my_grill.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved HTML successfully!")
else:
    print("Failed:", response.status_code)
