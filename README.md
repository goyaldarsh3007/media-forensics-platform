# Media Forensics Platform

Media Forensics Platform is a full-stack image investigation dashboard. It combines a React/Vite interface with a FastAPI service to surface signals associated with AI-generated images, metadata changes, and pixel-level manipulation.

The tool is intended for triage and investigation support. Its verdicts are indicators, not proof of image origin or authenticity.

## Features

- AI-generation scoring with the Hugging Face `Ateeqq/ai-vs-human-image-detector` model when available
- CIFAKE-trained PyTorch model as the local fallback detector
- EXIF metadata, image dimensions, file format, file size, SHA-256, and perceptual hash inspection
- Error Level Analysis (ELA) for compression inconsistencies and possible local edits
- Combined forensic assessment with verdict, confidence, score, summary, and contributing signals
- Session-only analyst login and in-session scan history in the frontend dashboard

## Architecture

```text
React + Vite frontend (port 5173)
              |
              | multipart POST /upload
              v
FastAPI backend (port 8000)
  |-- image metadata and hashes
  |-- pretrained/custom AI detector
  |-- Error Level Analysis
  `-- combined forensic assessor
```

## Repository Structure

```text
media-forensics/
├── backend/
│   ├── main.py                         # FastAPI app and upload endpoint
│   └── forensics/
│       ├── ai_detector.py               # Pretrained/custom AI scoring
│       ├── custom_ai_model.py           # CIFAKE model and training helpers
│       ├── forensic_assessor.py         # Combined verdict logic
│       ├── image_analyzer.py            # Metadata and hash extraction
│       ├── manipulation_detector.py     # ELA analysis
│       └── train_custom_ai_model.py     # Model preparation entry point
├── frontend/
│   ├── src/App.jsx                      # Login and investigation dashboard
│   └── package.json
├── models/custom_ai_vs_human_model.pth  # Local CIFAKE model weights
├── uploads/                             # Uploaded files and ELA outputs
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer and npm
- Enough disk space for PyTorch and the Hugging Face model cache
- Optional internet access on first backend startup to download model assets

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/goyaldarsh3007/media-forensics-platform.git
cd media-forensics-platform
```

### 2. Set up the Python backend

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up the frontend

```bash
cd frontend
npm install
cd ..
```

### 4. Start the backend

From the repository root, with the virtual environment activated:

```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Start the frontend

Open a second terminal:

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

Open `http://localhost:5173` and use the demo credentials shown on the login screen. The frontend calls the backend at `http://127.0.0.1:8000`.

## Model Behavior

The backend initializes the AI detector when it starts. It first attempts to load the Hugging Face model `Ateeqq/ai-vs-human-image-detector`. If that model cannot be loaded, the bundled CIFAKE model at `models/custom_ai_vs_human_model.pth` is used.

If the local model file is missing, the backend attempts to download the CIFAKE dataset through `kagglehub` and train a replacement. This can take a long time and requires network access. To prepare the local model explicitly:

```bash
python -m backend.forensics.train_custom_ai_model
```

## API

### `GET /`

Health-style response confirming that the API is running.

### `POST /upload`

Accepts an image as a multipart form field named `file` and returns metadata, AI detection, manipulation detection, and the combined forensic assessment.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/upload -F "file=@path/to/image.jpg"
```

The API also serves uploaded and generated files from `/uploads/<filename>`.

## Development Commands

Run frontend linting and a production build from `frontend/`:

```bash
npm run lint
npm run build
```

## Troubleshooting

- **Frontend cannot connect:** confirm the FastAPI server is running on port `8000`.
- **Model startup is slow:** the first run may download and cache model files.
- **Model download fails:** check network access, install all requirements, or ensure `models/custom_ai_vs_human_model.pth` exists.
- **PowerShell blocks activation:** run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` for the current terminal, then activate the environment again.

## Limitations

- The login is a client-side demo gate, not production authentication.
- Scan history is stored only in React memory and is lost when the page reloads.
- Results depend on model confidence, image format, metadata availability, and compression history.
- Uploaded files are written to `uploads/`; do not expose this development server publicly without adding authentication, validation, storage controls, and deployment hardening.
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
