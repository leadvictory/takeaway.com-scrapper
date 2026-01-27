import requests
import json

url = "https://globalmenucdn.eu-central-1.production.jet-external.com/annemax-14_nl_manifest.json"

headers = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.thuisbezorgd.nl/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()

    # Save to file
    with open("itemDetails.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("JSON saved successfully as itemDetails.json")
else:
    print("Request failed:", response.status_code, response.text)
