from PIL import Image
from transformers import pipeline


print("Loading AI image detector...")

detector = pipeline(
    "image-classification",
    model="capcheck/ai-human-generated-image-detection"
)

print("AI image detector loaded.")


def detect_ai_image(image_path):
    """
    Analyze an image for AI-generation indicators.
    """

    image = Image.open(image_path).convert("RGB")

    results = detector(image)

    return results