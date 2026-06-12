import os
import time
import requests
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

# Setup headless browser
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# Prepare image folder
if not os.path.exists('images'):
    os.makedirs('images')

# Read titles
with open('titles.txt', 'r', encoding='utf-8') as f:
    titles = [line.strip() for line in f if line.strip()]

# Start browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_page_load_timeout(90)

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def resize_and_save_image(url, filename):
    try:
        response = requests.get(url, timeout=30)
        image = Image.open(BytesIO(response.content))

        # Convert if transparent
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image = image.resize((500, 500))
        image.save(filename, format='JPEG')
        print(f"📥 Image downloaded and resized to 500x500: {filename}")
    except Exception as e:
        print(f"❌ Failed to download or resize image: {e}")

# Main logic
for title in titles:
    print(f"\n🔍 Searching for: {title}")
    query = '+'.join(title.split())
    search_url = f"https://aromaexclusive.com/search?q={query}"

    try:
        driver.get(search_url)
        time.sleep(2)
    except Exception as e:
        print(f"❌ Failed to load page: {e}")
        continue

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.find_all('div', class_='product-collection', attrs={'data-js-product': True})
    print(f"✅ Found {len(cards)} cards")

    best_match = None
    best_score = 0
    best_img_url = None
    best_card_title = ""

    for card in cards:
        title_tag = card.select_one('div.product-collection__title h2 a')
        if not title_tag:
            continue

        card_title = title_tag.text.strip()
        score = similar(card_title, title)

        if score > best_score:
            best_score = score
            best_match = card
            best_card_title = card_title
            img_tag = card.select_one('div.media a img')
            if img_tag and img_tag.has_attr('src'):
                best_img_url = "https:" + img_tag['src'].split("?")[0]

    # Final decision
    if best_score >= 0.85 and abs(len(best_card_title) - len(title)) <= 2:
        print(f"🎯 Match found: {best_card_title} ({round(best_score * 100, 1)}%)")
        filename = os.path.join("images", title.replace(" ", "_") + ".jpg")
        resize_and_save_image(best_img_url, filename)
    elif best_img_url:
        print(f"❌ No strong match found.")
        print(f"🤔 Closest match: {best_card_title} ({round(best_score * 100, 1)}%)")
        confirm = input(f"✅ Do you want to accept this match? (yes/no): ").strip().lower()

        if confirm == "yes":
            filename = os.path.join("images", title.replace(" ", "_") + ".jpg")
            resize_and_save_image(best_img_url, filename)
        elif confirm == "no":
            img_url = input(f"🔗 Enter image URL for '{title}' (or press Enter to skip): ").strip()
            if img_url:
                filename = os.path.join("images", title.replace(" ", "_") + ".jpg")
                resize_and_save_image(img_url, filename)
            else:
                print("⏩ Skipped by user.")
        else:
            print("⏩ Skipped by user.")
    else:
        print(f"❌ No matching product found.")
        img_url = input(f"🔗 Enter image URL for '{title}' (or press Enter to skip): ").strip()
        if img_url:
            filename = os.path.join("images", title.replace(" ", "_") + ".jpg")
            resize_and_save_image(img_url, filename)
        else:
            print("⏩ Skipped by user.")

driver.quit()
