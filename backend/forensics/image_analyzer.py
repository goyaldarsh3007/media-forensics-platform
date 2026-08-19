from PIL import Image
import imagehash
import exifread
import hashlib
import os


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            data = file.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def calculate_perceptual_hash(file_path):
    image = Image.open(file_path)

    phash = imagehash.phash(image)

    return str(phash)


def extract_metadata(file_path):
    metadata = {}

    with open(file_path, "rb") as file:
        tags = exifread.process_file(file, details=False)

    for tag, value in tags.items():

        if tag.startswith("Image") or tag.startswith("EXIF"):
            metadata[tag] = str(value)

    return metadata


def analyze_image(file_path):

    image = Image.open(file_path)

    file_size = os.path.getsize(file_path)

    sha256 = calculate_sha256(file_path)

    perceptual_hash = calculate_perceptual_hash(file_path)

    metadata = extract_metadata(file_path)

    result = {
        "filename": os.path.basename(file_path),

        "file_size_bytes": file_size,

        "format": image.format,

        "width": image.width,

        "height": image.height,

        "mode": image.mode,

        "sha256": sha256,

        "perceptual_hash": perceptual_hash,

        "metadata": metadata
    }

    return result