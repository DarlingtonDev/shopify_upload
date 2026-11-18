
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# PARFUM DEN - SHOPIFY CSV GENERATOR
# ============================================================

INPUT_JSON_FILE = "products.json"
TEMPLATE_CSV_FILE = "product_template (5).csv"
OUTPUT_CSV_FILE = "parfum_den_shopify_ready.csv"

# Fixed Parfum Den product values
VENDOR = "Parfum Den"
PRODUCT_CATEGORY = (
    "Health & Beauty > Personal Care > Cosmetics > Perfumes & Colognes"
)
PRODUCT_TYPE = "Perfume"

PUBLISHED = "True"
STATUS = "Active"

OPTION1_NAME = "Size"

CHARGE_TAX = "True"

INVENTORY_TRACKER = "shopify"
INVENTORY_QUANTITY = "12"
CONTINUE_SELLING = "DENY"

WEIGHT_GRAMS = "200"
WEIGHT_UNIT = "g"

REQUIRES_SHIPPING = "True"
FULFILLMENT_SERVICE = "manual"

IMAGE_POSITION = "1"
GIFT_CARD = "False"

GOOGLE_PRODUCT_CATEGORY = "Health & Beauty > Fragrances > Perfume"
GOOGLE_CONDITION = "New"

# SKU settings: preserve the existing four-minute increment.
SKU_PREFIX = "ParfumDen"
BASE_DATETIME = datetime.now()


# These are actual Shopify product fields required by this generator.
# The template's leading "index" column, if present, is a spreadsheet
# row index rather than a Shopify product field, so it is not exported.
REQUIRED_TEMPLATE_COLUMNS = {
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
    "Variant Barcodes",
    "Option1 name",
    "Option1 value",
    "Option1 Linked To",
    "Option2 name",
    "Option2 value",
    "Option2 Linked To",
    "Option3 name",
    "Option3 value",
    "Option3 Linked To",
    "Price",
    "Compare-at price",
    "Cost per item",
    "Charge tax",
    "Tax code",
    "Unit price total measure",
    "Unit price total measure unit",
    "Unit price base measure",
    "Unit price base measure unit",
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
    "Variant image URL",
    "Gift card",
    "SEO title",
    "SEO description",
    "Color (product.metafields.shopify.color-pattern)",
    "Google Shopping / Google product category",
    "Google Shopping / Gender",
    "Google Shopping / Age group",
    "Google Shopping / Manufacturer part number (MPN)",
    "Google Shopping / Ad group name",
    "Google Shopping / Ads labels",
    "Google Shopping / Condition",
    "Google Shopping / Custom product",
    "Google Shopping / Custom label 0",
    "Google Shopping / Custom label 1",
    "Google Shopping / Custom label 2",
    "Google Shopping / Custom label 3",
    "Google Shopping / Custom label 4",
    "Packed product length",
    "Packed product width",
    "Packed product height",
    "Packed product dimension unit",
}

REQUIRED_PRODUCT_FIELDS = [
    "title",
    "handle",
    "description",
    "tags",
    "size",
    "price",
    "compare at price",
    "image",
]


def load_template_headers(template_path):
    """Read the template's exact column order and exclude its row-index column."""
    path = Path(template_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Template file not found: {template_path}. "
            "Put the Shopify template in the same folder as this script."
        )

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        headers = next(reader, None)

    if not headers:
        raise ValueError("The Shopify template is empty or has no header row.")

    # Remove accidental whitespace and a possible spreadsheet index column.
    headers = [header.strip() for header in headers]
    headers = [
        header for header in headers
        if header.lower() not in {"index", "unnamed: 0"}
    ]

    missing_columns = REQUIRED_TEMPLATE_COLUMNS - set(headers)
    if missing_columns:
        raise ValueError(
            "The template is missing expected Shopify columns: "
            + ", ".join(sorted(missing_columns))
        )

    return headers


def load_products(json_path):
    """Load and validate the product JSON array."""
    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Product JSON file not found: {json_path}"
        )

    with path.open("r", encoding="utf-8") as file:
        products = json.load(file)

    if not isinstance(products, list):
        raise ValueError(
            f"{json_path} must contain a JSON array of product objects."
        )

    if not products:
        raise ValueError("The product JSON array is empty.")

    for index, product in enumerate(products, start=1):
        if not isinstance(product, dict):
            raise ValueError(
                f"Product {index} must be a JSON object."
            )

        missing_fields = [
            field for field in REQUIRED_PRODUCT_FIELDS
            if field not in product
        ]

        if missing_fields:
            raise ValueError(
                f"Product {index} is missing fields: {missing_fields}"
            )

        if not str(product["title"]).strip():
            raise ValueError(f"Product {index} has an empty title.")

        if not str(product["size"]).strip():
            raise ValueError(
                f"Product {index} has an empty size. "
                "Each perfume must have its actual bottle size."
            )

        if str(product["price"]).strip() == "":
            raise ValueError(f"Product {index} has an empty reseller price.")

        if str(product["compare at price"]).strip() == "":
            raise ValueError(f"Product {index} has an empty retail price.")

    return products


def make_seo_title(title):
    """Keep the existing Parfum Den SEO-title format."""
    return (
        f"{title} wholesale in Nigeria | "
        "Bulk perfume supplier | Parfum Den"
    )


def make_seo_description(title):
    """Keep the existing Parfum Den SEO-description format."""
    return (
        f"Buy {title} in bulk from Parfum Den. "
        "Trusted wholesale perfume supplier offering authentic "
        "fragrances, competitive prices, dropshipping, and "
        "nationwide delivery in Nigeria."
    )


def build_product_row(product, index, headers):
    """Map one JSON product into the Shopify template columns."""
    title = str(product["title"]).strip()

    timestamp = (
        BASE_DATETIME + timedelta(minutes=index * 4)
    ).strftime("%Y%m%d_%H%M%S")

    sku = f"{SKU_PREFIX}_{timestamp}"

    # Start with every template field blank. This preserves all columns
    # while leaving irrelevant or unknown fields empty.
    row = {header: "" for header in headers}

    row.update({
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

        # This batch uses bottle size as its variant option.
        "Option1 name": OPTION1_NAME,
        "Option1 value": product["size"],

        # Correct price mapping:
        # reseller price -> Shopify Price
        # retail price -> Shopify Compare-at price
        "Price": product["price"],
        "Compare-at price": product["compare at price"],

        # Do not put retail price in Cost per item.
        # It remains blank because actual product cost is unknown.
        "Cost per item": "",

        "Charge tax": CHARGE_TAX,
        "Inventory tracker": INVENTORY_TRACKER,
        "Inventory quantity": INVENTORY_QUANTITY,
        "Continue selling when out of stock": CONTINUE_SELLING,
        "Weight value (grams)": WEIGHT_GRAMS,
        "Weight unit for display": WEIGHT_UNIT,
        "Requires shipping": REQUIRES_SHIPPING,
        "Fulfillment service": FULFILLMENT_SERVICE,

        # The image uploader is expected to populate this JSON field.
        "Product image URL": product["image"],
        "Image position": IMAGE_POSITION,
        "Image alt text": title,

        "Gift card": GIFT_CARD,
        "SEO title": make_seo_title(title),
        "SEO description": make_seo_description(title),
        "Google Shopping / Google product category": (
            GOOGLE_PRODUCT_CATEGORY
        ),
        "Google Shopping / Condition": GOOGLE_CONDITION,
    })

    return row


def main():
    headers = load_template_headers(TEMPLATE_CSV_FILE)
    products = load_products(INPUT_JSON_FILE)

    rows = [
        build_product_row(product, index, headers)
        for index, product in enumerate(products)
    ]

    with open(
        OUTPUT_CSV_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=headers,
            extrasaction="raise"
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone! Generated {OUTPUT_CSV_FILE}")
    print(f"Total products: {len(rows)}")
    print(f"Shopify columns: {len(headers)}")
    print(
        "Price mapping: reseller price -> Price; "
        "retail price -> Compare-at price; "
        "Cost per item -> blank"
    )


if __name__ == "__main__":
    main()
