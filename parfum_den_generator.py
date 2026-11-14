
import json
import csv
from datetime import datetime, timedelta

INPUT_JSON_FILE = "products.json"
OUTPUT_CSV_FILE = "parfum_den_shopify_ready.csv"

# Fixed product values
VENDOR = "Parfum Den"
PRODUCT_CATEGORY = "Health & Beauty > Personal Care > Cosmetics > Perfumes & Colognes"
PRODUCT_TYPE = "Perfume"

PUBLISHED = "TRUE"
STATUS = "active"

OPTION1_NAME = "Size"

CHARGE_TAX = "TRUE"

INVENTORY_TRACKER = "shopify"
INVENTORY_QUANTITY = "12"
CONTINUE_SELLING = "DENY"

WEIGHT_GRAMS = "200"
WEIGHT_UNIT = "g"

REQUIRES_SHIPPING = "TRUE"
FULFILLMENT_SERVICE = "manual"

IMAGE_POSITION = "1"
GIFT_CARD = "FALSE"

GOOGLE_PRODUCT_CATEGORY = "Health & Beauty > Fragrances > Perfume"
GOOGLE_CONDITION = "new"

# SKU settings
SKU_PREFIX = "ParfumDen"
BASE_DATETIME = datetime.now()

# Read products
with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

if not isinstance(products, list):
    raise ValueError("products.json must contain a JSON array of products.")

# Required object fields
required_fields = [
    "title",
    "handle",
    "description",
    "tags",
    "size",
    "price",
    "cost per item",
    "image"
]

headers = [
    "Title",
    "URL handle",
    "Description",
    "Vendor",
    "Product category",
    "Type",
    "Tags",
    "Published on online store",
    "Status",
    "SKU",
    "Price",
    "Cost per item",
    "Product image URL",
    "Image alt text",
    "SEO title",
    "SEO description",
    "Option1 name",
    "Option1 value",
    "Charge tax",
    "Inventory tracker",
    "Inventory quantity",
    "Continue selling when out of stock",
    "Weight value (grams)",
    "Weight unit for display",
    "Requires shipping",
    "Fulfillment service",
    "Image position",
    "Gift card",
    "Google Shopping / Google product category",
    "Google Shopping / Condition"
]

rows = []

for idx, product in enumerate(products):

    # Check that the product object has all required fields
    missing_fields = [
        field for field in required_fields
        if field not in product
    ]

    if missing_fields:
        raise ValueError(
            f"Product {idx + 1} is missing fields: {missing_fields}"
        )

    title = product["title"]

    # Generate SKU with a 4-minute increment
    timestamp = (
        BASE_DATETIME + timedelta(minutes=idx * 4)
    ).strftime("%Y%m%d_%H%M%S")

    sku = f"{SKU_PREFIX}_{timestamp}"

    # Generate SEO metadata
    seo_title = (
        f"{title} wholesale in Nigeria | "
        "Bulk perfume supplier | Parfum Den"
    )

    seo_description = (
        f"Buy {title} in bulk from Parfum Den. "
        "Trusted wholesale perfume supplier offering authentic "
        "fragrances, competitive prices, dropshipping, and "
        "nationwide delivery in Nigeria."
    )

    row = {
        "Title": title,
        "URL handle": product["handle"],
        "Description": product["description"],
        "Vendor": VENDOR,
        "Product category": PRODUCT_CATEGORY,
        "Type": PRODUCT_TYPE,
        "Tags": product["tags"],
        "Published on online store": PUBLISHED,
        "Status": STATUS,
        "SKU": sku,
        "Price": product["price"],
        "Cost per item": product["cost per item"],
        "Product image URL": product["image"],
        "Image alt text": title,
        "SEO title": seo_title,
        "SEO description": seo_description,
        "Option1 name": OPTION1_NAME,
        "Option1 value": product["size"],
        "Charge tax": CHARGE_TAX,
        "Inventory tracker": INVENTORY_TRACKER,
        "Inventory quantity": INVENTORY_QUANTITY,
        "Continue selling when out of stock": CONTINUE_SELLING,
        "Weight value (grams)": WEIGHT_GRAMS,
        "Weight unit for display": WEIGHT_UNIT,
        "Requires shipping": REQUIRES_SHIPPING,
        "Fulfillment service": FULFILLMENT_SERVICE,
        "Image position": IMAGE_POSITION,
        "Gift card": GIFT_CARD,
        "Google Shopping / Google product category": GOOGLE_PRODUCT_CATEGORY,
        "Google Shopping / Condition": GOOGLE_CONDITION
    }

    rows.append(row)

# Generate Shopify CSV
with open(
    OUTPUT_CSV_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nDone! Generated {OUTPUT_CSV_FILE}")
print(f"Total products: {len(rows)}")
