from pathlib import Path

from PIL import Image
from transformers import pipeline

from backend.forensics.custom_ai_model import ensure_model_exists, predict_ai_probability


PRETRAINED_MODEL = "Ateeqq/ai-vs-human-image-detector"

print("Loading pretrained AI image detector...")
try:
    detector = pipeline("image-classification", model=PRETRAINED_MODEL)
    print("Pretrained AI image detector loaded.")
except Exception as error:
    detector = None
    print(f"Pretrained AI detector unavailable; using custom detector only: {error}")

ensure_model_exists()


def _pretrained_ai_probability(image_path: str | Path) -> float:
    if detector is None:
        return 0.0

    results = detector(Image.open(image_path).convert("RGB"))
    ai_probability = next(
        (
            result["score"]
            for result in results
            if result["label"].lower() in {"ai", "fake", "synthetic", "ai-generated"}
        ),
        0.0,
    )
    return float(min(1.0, max(0.0, ai_probability)))


def detect_ai_image(image_path):
    """Use the pretrained detector, with the CIFAKE model as a fallback."""
    custom_probability = predict_ai_probability(image_path)
    pretrained_probability = _pretrained_ai_probability(image_path)

    if detector is None:
        ai_probability = custom_probability
    else:
        ai_probability = pretrained_probability

    results = [
        {"label": "AI", "score": float(ai_probability)},
        {"label": "Human", "score": float(1.0 - ai_probability)},
    ]

    print("\nCOMBINED AI DETECTOR RESULT:")
    print(results)
    return results