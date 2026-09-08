from backend.forensics.custom_ai_model import ensure_model_exists, predict_ai_probability


print("Loading custom AI image detector...")
ensure_model_exists()
print("Custom AI image detector loaded.")


def detect_ai_image(image_path):
    """
    Analyze an image for AI-generation indicators using a custom-trained CNN.
    """
    ai_probability = predict_ai_probability(image_path)
    human_probability = 1.0 - ai_probability

    results = [
        {"label": "AI", "score": float(ai_probability)},
        {"label": "Human", "score": float(human_probability)},
    ]

    print("\nRAW CUSTOM AI DETECTOR RESULT:")
    print(results)
    return results