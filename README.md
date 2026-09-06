# Media Forensics Platform

A full-stack web application for analyzing uploaded images to detect possible AI-generated content, metadata inconsistencies, and digital tampering. The system combines a Python FastAPI backend with a React frontend to provide a dashboard for media forensic investigation.

The project evaluates an image using multiple signals:

- AI generation probability using a Hugging Face image classification model
- EXIF metadata inspection for editing signatures and camera authenticity hints
- File structure and extension validation
- Error Level Analysis (ELA) to detect locally modified or spliced regions
- A combined forensic assessment that summarizes the result as a verdict with confidence

---

## Project Overview

This repository is designed for media authenticity analysis. It is especially useful for:

- checking whether an image looks AI-generated
- identifying signs of editing or tampering
- reviewing metadata clues left by camera devices or editing software
- spotting suspicious compression patterns using ELA
- presenting all findings in a user-friendly dashboard

The workflow is simple:

1. User uploads an image in the frontend
2. Backend saves the file to the uploads directory
3. Analysis modules extract metadata, detect AI patterns, and compute ELA
4. The forensic assessor combines all signals into a final verdict
5. Results are returned to the UI and shown in a dashboard

---

## Repository Structure

```text
media-forensics/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── forensics/
│       ├── __init__.py
│       ├── ai_detector.py
│       ├── forensic_assessor.py
│       ├── image_analyzer.py
│       └── manipulation_detector.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       └── main.jsx
├── uploads/
├── requirements.txt
├── .gitignore
├── README.md
└── venv/
```

### Key backend files

- `backend/main.py`  
  Defines the FastAPI app and the upload endpoint.

- `backend/forensics/ai_detector.py`  
  Loads the Hugging Face AI-vs-human image classification model and returns confidence scores.

- `backend/forensics/image_analyzer.py`  
  Extracts file metadata, dimensions, hash values, and image properties.

- `backend/forensics/manipulation_detector.py`  
  Runs Error Level Analysis (ELA) and produces a tampering score plus an ELA image.

- `backend/forensics/forensic_assessor.py`  
  Combines the different signals into a final verdict such as:
  - Likely AI-generated
  - Likely human-created
  - Suspicious / Manipulated
  - Uncertain

### Key frontend files

- `frontend/src/App.jsx`  
  Handles file selection, sending upload requests, and displaying processed results.

- `frontend/src/App.css`  
  Contains dashboard styling and media analysis presentation.

---

## How the System Works

### 1. Image upload
The user selects an image in the React app and clicks Analyze Media. The frontend sends a multipart form upload to the backend API endpoint:

```text
POST http://127.0.0.1:8000/upload
```

The server receives the file and stores it in the `uploads/` folder.

### 2. File analysis
The backend executes the following checks:

#### AI detection
The AI detector uses a pretrained transformer image-classification model:

- `Ateeqq/ai-vs-human-image-detector`

It returns outputs like:

- AI probability
- Human probability

These values help estimate whether the image looks synthetic or naturally created.

#### Metadata inspection
The image analyzer reads EXIF metadata and collects details such as:

- width and height
- file format
- file size
- SHA-256 hash
- perceptual hash
- EXIF camera and software tags

This helps identify:

- camera-originated content
- editing tools such as Photoshop or Canva
- stripped or incomplete metadata
- mismatched file structure signals

#### Manipulation detection
The ELA module resaves the image at a controlled JPEG quality level and compares it to the original. Areas with inconsistent compression patterns often indicate editing or compositing.

The result includes:

- ELA score
- max block variance
- ratio values
- verdict
- status
- output ELA image file name

### 3. Forensic assessment
The forensic assessor combines multiple indicators into a single verdict. It evaluates:

- AI score
- metadata integrity
- file extension vs actual format mismatch
- ELA/tampering indicators

It returns a structured result like:

```json
{
  "verdict": "Likely AI-generated",
  "confidence": "High",
  "summary_text": "Neural analysis strongly indicates synthetic patterns...",
  "score": 0.92,
  "signals": {
    "ai_generation": {...},
    "metadata_integrity": {...},
    "file_structure": {...},
    "pixel_manipulation": {...}
  }
}
```

---

## Tech Stack

### Backend
- Python
- FastAPI
- Pillow
- NumPy
- ImageHash
- ExifRead
- Transformers
- PyTorch
- Uvicorn

### Frontend
- React
- Vite
- JavaScript

---

## How to Run the Project

### 1. Clone the repository
```bash
git clone https://github.com/goyaldarsh3007/media-forensics-platform.git
cd media-forensics-platform
```

### 2. Create and activate a Python virtual environment

#### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Install frontend dependencies
```bash
cd frontend
npm install
cd ..
```

### 5. Start the backend
From the project root:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

This runs the FastAPI server.

### 6. Start the frontend
In a separate terminal from the project root:

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

### 7. Open the app
Visit:

```text
http://localhost:5173
```

The frontend communicates with:

```text
http://127.0.0.1:8000
```

---

## API Endpoint

### Upload endpoint
```text
POST /upload
```

Request:
- multipart form-data
- field name: `file`

Response:
- analysis data
- AI detection data
- manipulation detection data
- final forensic assessment

Example response structure:

```json
{
  "message": "Forensic analysis completed.",
  "analysis": {...},
  "ai_detection": {...},
  "manipulation_detection": {...},
  "forensic_assessment": {...}
}
```

---

## Typical Usage Flow

1. Open the frontend dashboard in the browser
2. Select a photo or image file
3. Click Analyze Media
4. Wait for the pipeline to process the file
5. Review the results panel for:
   - summary verdict
   - AI probability
   - metadata details
   - ELA heatmap status
   - confidence score and explanation
6. Repeat with other images for comparison

---

## Notes on Behavior

- The app is optimized for image analysis, not video
- Uploaded files are stored in the `uploads/` folder temporarily for processing
- The ELA module generates sidecar images like `filename_ela.jpg` for visual inspection
- The AI model may download from Hugging Face the first time it runs, so the first load can take longer
- Some authentic images with heavy compression or social-media filtering may trigger uncertain or borderline classifications

---

## Important Files to Know

- `backend/main.py` — API entry point
- `backend/forensics/ai_detector.py` — AI detection model
- `backend/forensics/image_analyzer.py` — metadata and image summary
- `backend/forensics/manipulation_detector.py` — ELA tampering analysis
- `backend/forensics/forensic_assessor.py` — decision logic
- `frontend/src/App.jsx` — user interface and analysis flow

---

## Troubleshooting

### Backend not starting
Check that dependencies are installed:

```bash
pip install -r requirements.txt
```

Also verify that the virtual environment is active.

### Frontend not loading
Make sure the frontend dependencies are installed:

```bash
cd frontend
npm install
```

### Model download issue
The model may need internet access to download from Hugging Face. Ensure the environment has internet connectivity and no firewall restrictions.

### Upload failure
Verify that the backend is running on port 8000 and the frontend is pointing to the same host and port.

---

## License

This project is intended for educational, research, and forensic-analysis demonstration purposes.

---

## Summary

This repository provides a practical image-forensics workflow that combines AI detection, metadata analysis, and error-level analysis in a single dashboard. It is useful for digital investigation tasks, research experimentation, and demonstrating how forensic signals can be combined into an overall authenticity decision.
