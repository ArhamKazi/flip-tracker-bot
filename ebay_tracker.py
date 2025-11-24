import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1394324157952557200/_KmWAGnW1ojVPHvyGq3qSCZhZdBbOJ6s8gdwLFU-J1iIXYpua7w_KkN8TX1NVmSFQJii"
KEYWORD = "jordan"
MAX_PRICE = 100
REQUIRE_NEW = True  # Only show 'New' condition items


def search_ebay_static(keyword, max_price):
    print(f"🔍 Searching eBay for '{keyword}' under ${max_price} (New only)")
    url = f"https://www.ebay.com/sch/i.html?_nkw={keyword.replace(' ', '+')}&_sop=10&_udhi={max_price}&LH_BIN=1"

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    listings = soup.select("li.s-item")

    results = []
    for item in listings:
        title_elem = item.select_one(".s-item__title")
        price_elem = item.select_one(".s-item__price")
        link_elem = item.select_one("a.s-item__link")
        img_elem = item.select_one("img")
        condition_elem = item.select_one(".SECONDARY_INFO")

        if not (title_elem and price_elem and link_elem):
            continue

        condition = condition_elem.get_text().strip() if condition_elem else ""
        if REQUIRE_NEW and "New" not in condition:
            continue

        title = title_elem.get_text()
        price = price_elem.get_text()
        url = link_elem["href"]
        image = img_elem["src"] if img_elem else None

        try:
            price_num = float(price.replace("$", "").replace(",", "").split()[0])
            if price_num <= max_price:
                results.append({
                    "title": title,
                    "price": f"${price_num:.2f}",
                    "url": url,
                    "image": image,
                    "condition": condition
                })
        except:
            continue

    print(f"✅ Found {len(results)} new-condition listings")
    return results


def send_discord_alert(item):
    content = f"""🥿 **New Jordan Found on eBay!**
**Title**: {item['title']}
💸 **Price**: {item['price']}
📦 **Condition**: {item['condition']}
🔗 [View Listing]({item['url']})
"""
    payload = {"content": content}
    if item.get("image"):
        payload["embeds"] = [{"image": {"url": item["image"]}}]

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print(f"✅ Alert sent: {item['title']}")
    else:
        print(f"❌ Failed to send alert: {response.status_code} - {response.text}")


def main():
    items = search_ebay_static(KEYWORD, MAX_PRICE)
    for item in items:
        send_discord_alert(item)


if __name__ == "__main__":
    main()
