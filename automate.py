
import os
import json
import re
import unicodedata
from difflib import SequenceMatcher

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

# === NORMALIZATION ===
NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
}

IMPORTANT_TERMS = {
    "edp", "edt", "edc", "parfum", "parfume",
    "intense", "absolu", "absolut", "extreme",
    "blue", "red", "pink", "black", "white",
    "purple", "green", "gold", "silver",
    "pour", "femme", "homme", "women", "woman",
    "men", "man", "eau", "de", "toilette",
    "extract", "elixir", "essence",
}

def normalize(text):
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )

    text = text.lower().replace("&", " and ")
    text = text.replace("’", "'")

    # Normalize number words
    for word, number in NUMBER_WORDS.items():
        text = re.sub(rf"\b{word}\b", number, text)

    # Normalize measurements: 100 ml -> 100ml
    text = re.sub(r"(\d+)\s+(ml|oz)\b", r"\1\2", text)

    # Normalize punctuation and separators
    text = re.sub(r"[^a-z0-9]+", " ", text)

    return " ".join(text.split())


def tokens(text):
    return set(normalize(text).split())


def important_tokens(text):
    return tokens(text) & IMPORTANT_TERMS


def compatible(title, filename):
    title_tokens = tokens(title)
    file_tokens = tokens(filename)

    # Important product characteristics must not conflict.
    title_important = important_tokens(title)
    file_important = important_tokens(filename)

    if title_important != file_important:
        return False

    # Product identity must substantially overlap.
    common = title_tokens & file_tokens

    if not common:
        return False

    # Reject candidates missing too many identifying words.
    title_coverage = len(common) / max(len(title_tokens), 1)
    file_coverage = len(common) / max(len(file_tokens), 1)

    return title_coverage >= 0.85 and file_coverage >= 0.85


def find_best_match(title, filenames):
    normalized_title = normalize(title)

    candidates = []

    for filename in filenames:
        name_without_ext, extension = os.path.splitext(filename)

        if extension.lower() not in {
            ".jpg", ".jpeg", ".png", ".webp"
        }:
            continue

        normalized_filename = normalize(name_without_ext)

        # Exact match after normalization
        if normalized_filename == normalized_title:
            return filename

        if compatible(title, name_without_ext):
            title_words = set(normalized_title.split())
            file_words = set(normalized_filename.split())

            overlap = len(title_words & file_words)
            score = overlap / max(len(title_words | file_words), 1)

            candidates.append((score, filename))

    if not candidates:
        return None

    candidates.sort(reverse=True)

    best_score, best_filename = candidates[0]

    # Require a strong match
    if best_score < 0.85:
        return None

    # Do not guess if two candidates are equally plausible
    if len(candidates) > 1:
        second_score, _ = candidates[1]

        if best_score - second_score < 0.05:
            return None

    return best_filename


# === LOAD PRODUCTS ===
with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

if not isinstance(products, list):
    raise ValueError("input.json must contain a JSON array of products.")

# === LOAD IMAGE FILENAMES ONCE ===
image_files = os.listdir(IMAGES_FOLDER)

# === PROCESS PRODUCTS ===
updated_products = []

for product in products:
    title = product.get("title", "").strip()

    matched_file = find_best_match(title, image_files)

    if matched_file:
        image_path = os.path.join(IMAGES_FOLDER, matched_file)

        print(f"📤 Uploading: {matched_file}")

        try:
            upload_result = cloudinary.uploader.upload(
                image_path,
                folder="shopify-products",
                public_id=normalize(title).replace(" ", "-"),
                overwrite=True,
                resource_type="image"
            )

            product["image"] = upload_result["secure_url"]

        except Exception as e:
            print(f"❌ Failed to upload {matched_file}: {e}")
            product["image"] = ""

    else:
        print(f"⚠️ No confident image match for: {title}")
        product["image"] = ""

    updated_products.append(product)


# === SAVE FINAL JSON ===
with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(updated_products, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done! Created {OUTPUT_JSON_FILE} with image URLs.")
