from pathlib import Path

from backend.forensics.custom_ai_model import ensure_model_exists, MODEL_PATH


if __name__ == "__main__":
    output = ensure_model_exists(MODEL_PATH)
    print(f"Training complete. Model saved at: {output}")
