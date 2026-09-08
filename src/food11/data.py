from pathlib import Path
from PIL import Image
import shutil

CATEGORIES = {
    "0": "Bread",
    "1": "Dairy product",
    "2": "Dessert",
    "3": "Egg",
    "4": "Fried food",
    "5": "Meat",
    "6": "Noodles-Pasta",
    "7": "Rice",
    "8": "Seafood",
    "9": "Soup",
    "10": "Vegetable-Fruit",
}

RAW_DIR = Path("data/food11_raw")
PROCESSED_DIR = Path("data/food11_processed")
MINI_DIR = Path("data/food11_processed_mini")

SPLITS = ["training", "evaluation", "validation"]


def prepare_output_folders():
    for output_dir in [PROCESSED_DIR, MINI_DIR]:
        if output_dir.exists():
            shutil.rmtree(output_dir)

        for split in SPLITS:
            for category in CATEGORIES.values():
                (output_dir / split / category).mkdir(
                    parents=True,
                    exist_ok=True
                )


def process_split(split):
    mini_counts = {category: 0 for category in CATEGORIES.values()}

    input_dir = RAW_DIR / split

    for image_path in input_dir.iterdir():
        if not image_path.is_file():
            continue

        label = image_path.name.split("_")[0]

        if label not in CATEGORIES:
            continue

        category = CATEGORIES[label]

        try:
            with Image.open(image_path) as image:
                image = image.convert("RGB")
                image = image.resize((128, 128))

                processed_path = (
                    PROCESSED_DIR
                    / split
                    / category
                    / image_path.name
                )

                image.save(processed_path)

                if mini_counts[category] < 100:
                    mini_path = (
                        MINI_DIR
                        / split
                        / category
                        / image_path.name
                    )

                    image.save(mini_path)
                    mini_counts[category] += 1

        except Exception as e:
            print(f"Could not process {image_path}: {e}")


def main():
    prepare_output_folders()

    for split in SPLITS:
        print(f"Processing {split}...")
        process_split(split)

    print("Data preparation finished.")


if __name__ == "__main__":
    main()