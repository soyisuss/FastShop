from pathlib import Path
from PIL import Image, UnidentifiedImageError


def clean_broken_images(dataset_dir="data"):
    dataset_dir = Path(dataset_dir)
    count = 0
    for img_path in dataset_dir.rglob("*.*"):
        try:
            with Image.open(img_path) as img:
                img.verify()
        except (UnidentifiedImageError, OSError):
            print(f"Eliminando imagen inválida: {img_path}")
            img_path.unlink()
            count += 1
    print(f"Total eliminadas: {count}")


if __name__ == "__main__":
    clean_broken_images()
