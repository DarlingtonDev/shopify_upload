import json
import csv
from datetime import datetime, timedelta

# === CONFIGURATION ===
INPUT_JSON_FILE = "products.json"
OUTPUT_CSV_FILE = "shopify_ready.csv"

# Static values
FIXED_QUANTITY = 7
FIXED_WEIGHT_GRAMS = 500  # 0.5kg = 500g
BASE_DATETIME = datetime.now()
PUBLISH_STATUS = "TRUE"
STATUS = "active"
VENDOR_NAME = "The Scents Store"
OPTION1_NAME = "Title"
OPTION1_VALUE = "Default Title"
DEFAULT_CATEGORY = "Health & Beauty > Personal Care > Cosmetics > Perfumes & Colognes > Eaux de Parfum"

# === LOAD JSON PRODUCTS ===
with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

# === HEADERS MATCHING SHOPIFY EXPORT ===
headers = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published",
    "Option1 Name", "Option1 Value", "Variant SKU", "Variant Grams", "Variant Inventory Tracker",
    "Variant Inventory Qty", "Variant Inventory Policy", "Variant Fulfillment Service",
    "Variant Price", "Variant Requires Shipping", "Variant Taxable", "Image Src",
    "SEO Title", "SEO Description", "Status"
]

rows = []

# === BUILD EACH PRODUCT ROW ===
for idx, product in enumerate(products):
    timestamp = (BASE_DATETIME + timedelta(minutes=idx * 4)).strftime("%Y%m%d_%H%M%S")
    handle = product["title"].lower().replace(" ", "-").replace("'", "").replace(",", "").replace(".", "")
    sku = f'{product["brand"]}_{timestamp}'
    seo_title = f'{product["title"]} | Buy Online Nigeria'
    seo_description = (
        f'Shop for {product["title"]} Online at best prices on TheScentsStore.com. '
        f'Large selection of perfumes by {product["brand"]}. Order now!'
    )

    row = [
    handle,
    product["title"],
    product["description"],
    VENDOR_NAME,
    DEFAULT_CATEGORY,
    "",  # Type left blank
    product["tags"],
    PUBLISH_STATUS,
    OPTION1_NAME,
    OPTION1_VALUE,
    sku,
    str(FIXED_WEIGHT_GRAMS),
    "shopify",
    str(FIXED_QUANTITY),
    "deny",
    "manual",
    str(product["price"]),
    "TRUE",
    "TRUE",
    product.get("image", ""),  # ✅ Now pulls image URL from JSON
    seo_title,
    seo_description,
    STATUS
]

    rows.append(row)

# === WRITE TO CSV FILE ===
with open(OUTPUT_CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"\n✅ Done! CSV file generated: {OUTPUT_CSV_FILE}")
