"""Validate a processed Food-11 dataset against the data contract."""
import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image

from src.food11.data import CLASSES, SPLITS

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def list_images(root: Path) -> dict:
    """{split: {class: [image paths]}}; missing folders give empty lists."""
    images = {}
    for split in SPLITS:
        images[split] = {}
        for category in CLASSES:
            folder = root / split / category
            images[split][category] = (
                sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
                if folder.is_dir()
                else []
            )
    return images


def check_class_folders(root: Path) -> list:
    problems = []
    for split in SPLITS:
        split_dir = root / split
        found = {p.name for p in split_dir.iterdir() if p.is_dir()} if split_dir.is_dir() else set()
        if found != set(CLASSES):
            problems.append(
                f"{split}: missing {sorted(set(CLASSES) - found)}, extra {sorted(found - set(CLASSES))}"
            )
    return problems


def check_images(images: dict) -> list:
    problems = []
    for classes in images.values():
        for paths in classes.values():
            for path in paths:
                try:
                    with Image.open(path) as img:
                        img.load()  # force a full decode, catches truncated files
                        if img.mode != "RGB" or img.size != (128, 128):
                            problems.append(f"{path}: mode={img.mode} size={img.size}")
                except OSError as e:
                    problems.append(f"{path}: cannot open ({e})")
    return problems


def check_min_per_class(images: dict, minimum: int) -> list:
    return [
        f"{split}/{category}: {len(paths)} images < {minimum}"
        for split, classes in images.items()
        for category, paths in classes.items()
        if len(paths) < minimum
    ]


def check_no_leakage(images: dict) -> list:
    problems = []
    seen = {}  # content hash -> (split, path) of the first image with that content
    for split in SPLITS:
        for paths in images[split].values():
            for path in paths:
                digest = hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()
                if digest in seen and seen[digest][0] != split:
                    problems.append(f"{path} is identical to {seen[digest][1]}")
                seen.setdefault(digest, (split, path))
    return problems


def check_class_balance(images: dict, tau: float) -> list:
    train_total = sum(len(p) for p in images["training"].values())
    val_total = sum(len(p) for p in images["validation"].values())
    if not train_total or not val_total:
        return ["training or validation split is empty"]
    problems = []
    for category in CLASSES:
        train_share = len(images["training"][category]) / train_total
        val_share = len(images["validation"][category]) / val_total
        gap = abs(train_share - val_share)
        if gap > tau:
            problems.append(
                f"{category}: train {train_share:.3f} vs val {val_share:.3f} (gap {gap:.3f} > {tau})"
            )
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="e.g. data/food11_processed_mini")
    parser.add_argument("--min-per-class", type=int, default=50)
    parser.add_argument("--tau", type=float, default=0.05)
    args = parser.parse_args()

    if not args.root.is_dir():
        sys.exit(f"Not a directory: {args.root}")

    images = list_images(args.root)
    checks = [
        ("each split has exactly the 11 class folders", check_class_folders(args.root)),
        ("every image opens, is RGB and 128x128", check_images(images)),
        (f"every class has >= {args.min_per_class} images", check_min_per_class(images, args.min_per_class)),
        ("no image appears in two splits", check_no_leakage(images)),
        (f"class shares train vs val within {args.tau}", check_class_balance(images, args.tau)),
    ]

    failed = False
    for name, problems in checks:
        status = f"FAIL ({len(problems)})" if problems else "PASS"
        print(f"{status}  {name}")
        for problem in problems[:5]:
            print(f"        {problem}")
        if len(problems) > 5:
            print(f"        ... and {len(problems) - 5} more")
        failed = failed or bool(problems)

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()