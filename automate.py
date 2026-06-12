import os
import json
import cloudinary
import cloudinary.uploader

# === CLOUDINARY CONFIG ===
cloudinary.config(
    cloud_name="dawmylbpo",
    api_key="164357818181474",
    api_secret="eyJ2EgviPMShl8-_dIyB9DzmGrc"
)

# === PATHS ===
INPUT_JSON_FILE = "input.json"
OUTPUT_JSON_FILE = "products.json"
IMAGES_FOLDER = "images"

# === LOAD PRODUCTS ===
with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

# === PROCESS PRODUCTS ===
updated_products = []

for product in products:
    title = product.get("title", "").strip().lower()
    matched_file = None

    for filename in os.listdir(IMAGES_FOLDER):
        name_without_ext, _ = os.path.splitext(filename)
        if name_without_ext.strip().lower().replace("-", " ") == title:
            matched_file = filename
            break

    if matched_file:
        image_path = os.path.join(IMAGES_FOLDER, matched_file)
        print(f"📤 Uploading: {matched_file}")
        try:
            upload_result = cloudinary.uploader.upload(
                image_path,
                folder="shopify-products",
                public_id=title.replace(" ", "-"),
                overwrite=True,
                resource_type="image"
            )
            product["image"] = upload_result["secure_url"]
        except Exception as e:
            print(f"❌ Failed to upload {matched_file}: {e}")
            product["image"] = ""
    else:
        print(f"⚠️ Image not found for: {title}")
        product["image"] = ""

    updated_products.append(product)

# === SAVE FINAL JSON ===
with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(updated_products, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done! Created {OUTPUT_JSON_FILE} with image URLs.")