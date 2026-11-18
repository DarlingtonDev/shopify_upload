
import json
import csv
from datetime import datetime, timedelta

INPUT_JSON_FILE = "products.json"
OUTPUT_CSV_FILE = "parfum_den_shopify_ready.csv"

# Only the Shopify columns we agreed to include.
HEADERS = [
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
    "Option1 name",
    "Option1 value",
    "Price",
    "Compare-at price",
    "Charge tax",
    "Inventory tracker",
    "Inventory quantity",
    "Continue selling when out of stock",
    "Weight value (grams)",
    "Weight unit for display",
    "Requires shipping",
    "Fulfillment service",
    "Product image URL",
    "Image position",
    "Image alt text",
    "Gift card",
    "SEO title",
    "SEO description",
    "Google Shopping / Google product category",
    "Google Shopping / Condition",
]

VENDOR = "Parfum Den"
PRODUCT_CATEGORY = (
    "Health & Beauty > Personal Care > Cosmetics > Perfumes & Colognes"
)
GOOGLE_PRODUCT_CATEGORY = "Health & Beauty > Fragrances > Perfume"


def generate_seo_title(title):
    return f"{title} wholesale in Nigeria | Bulk perfume supplier | Parfum Den"


def generate_seo_description(title):
    return (
        f"Buy {title} in bulk from Parfum Den. Trusted wholesale perfume "
        "supplier offering authentic fragrances, competitive prices, "
        "dropshipping, and nationwide delivery in Nigeria."
    )


def generate_sku(index):
    # Retains the four-minute interval between generated SKUs.
    sku_time = datetime.now() + timedelta(minutes=4 * index)
    return f"ParfumDen_{sku_time.strftime('%Y%m%d%H%M%S')}"


def validate_product(product, index):
    required_fields = [
        "title",
        "handle",
        "description",
        "tags",
        "size",
        "price",
        "compare at price",
        "image",
    ]

    missing = [
        field for field in required_fields
        if field not in product or str(product[field]).strip() == ""
    ]

    if missing:
        raise ValueError(
            f"Product {index + 1} ({product.get('title', 'Unknown')}): "
            f"Missing or empty fields: {', '.join(missing)}"
        )


def main():
    with open(INPUT_JSON_FILE, "r", encoding="utf-8") as file:
        products = json.load(file)

    if not isinstance(products, list):
        raise ValueError("products.json must contain a JSON list of products.")

    rows = []

    for index, product in enumerate(products):
        validate_product(product, index)

        row = {
            "Title": product["title"],
            "URL handle": product["handle"],
            "Description": product["description"],
            "Vendor": VENDOR,
            "Product category": PRODUCT_CATEGORY,
            "Type": "Perfume",
            "Tags": product["tags"],
            "Published on online store": "TRUE",
            "Status": "Active",
            "SKU": generate_sku(index),
            "Option1 name": "Size",
            "Option1 value": product["size"],
            "Price": product["price"],
            "Compare-at price": product["compare at price"],
            "Charge tax": "TRUE",
            "Inventory tracker": "shopify",
            "Inventory quantity": "12",
            "Continue selling when out of stock": "DENY",
            "Weight value (grams)": "200",
            "Weight unit for display": "g",
            "Requires shipping": "TRUE",
            "Fulfillment service": "manual",
            "Product image URL": product["image"],
            "Image position": "1",
            "Image alt text": product["title"],
            "Gift card": "FALSE",
            "SEO title": generate_seo_title(product["title"]),
            "SEO description": generate_seo_description(product["title"]),
            "Google Shopping / Google product category": GOOGLE_PRODUCT_CATEGORY,
            "Google Shopping / Condition": "New",
        }

        rows.append(row)

    with open(
        OUTPUT_CSV_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done! Generated {OUTPUT_CSV_FILE}")
    print(f"Total products: {len(rows)}")
    print(f"Shopify columns: {len(HEADERS)}")


if __name__ == "__main__":
    main()
