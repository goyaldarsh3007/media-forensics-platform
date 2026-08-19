from backend.forensics.ai_detector import detect_ai_image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from backend.forensics.image_analyzer import analyze_image
from backend.forensics.forensic_assessor import assess_forensics
from backend.forensics.manipulation_detector import detect_manipulation
from fastapi.staticfiles import StaticFiles
import os


app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():

    return {
        "message": "Media Forensics API is running!"
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        buffer.write(
            await file.read()
        )

    try:

        analysis = analyze_image(file_path)
        ai_results = detect_ai_image(file_path)
        ai_score = 0.0
        human_score = 0.0
        for result in ai_results:
            label = result["label"].lower()
            score = result["score"]

            if "ai" in label:
                ai_score = score
            elif "human" in label or label == "hum":
                human_score = score
        ai_detection = {
            "ai_probability": ai_score,
            "human_probability": human_score
        }
        # Perform image manipulation checks (Error Level Analysis)
        manipulation_detection = detect_manipulation(file_path)

        # Determine overall assessment using multi-signal Forensic Assessor
        forensic_assessment = assess_forensics(analysis, ai_detection, manipulation_detection)
        

        return {
            "message": "Forensic analysis completed.",
            "analysis": analysis,
            "ai_detection": ai_detection,
            "manipulation_detection": manipulation_detection,
            "forensic_assessment": forensic_assessment
        }

    except Exception as error:

        return {
            "message": "Analysis failed.",
            "error": str(error)
        }