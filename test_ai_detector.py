from backend.forensics.ai_detector import detect_ai_image


image_path = "uploads/verified_real_dog.jpg"

results = detect_ai_image(image_path)

print("\nAI DETECTION RESULTS")
print("--------------------")

for result in results:
    print(
        f"{result['label']}: "
        f"{result['score']:.4f}"
    )