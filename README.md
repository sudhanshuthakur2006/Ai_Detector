# StealthDoc — AI Text Detector & Document Analyzer

A high-performance, privacy-first AI text detection and document analysis platform designed to detect AI-generated academic prose, articles, and research papers with sentence-level neural classification.

---

## 🚀 Key Features

- **Dynamic Neural AI Detection**: Uses fine-tuned transformer classification (`DistilBERT` model) with zero hardcoded phrases.
- **Document Support (.docx & .txt)**: Upload Word or Plain Text documents while preserving original formatting, headings, and paragraph structure.
- **Sentence-Level AI Highlighting**: Visual indicators pinpoint exact sentences flagged by academic AI detection algorithms (calibrated against Turnitin and iThenticate patterns).
- **Interactive Analytics Dashboard**: Real-time breakdown of Human %, AI %, and Mixed Content with interactive pie charts.
- **Privacy-First**: Run entirely on your local machine.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Hugging Face Transformers, PyTorch, Python-docx
- **Frontend**: React 19, Vite, Tailwind CSS, Lucide React, Recharts, Axios

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

The backend API will run at `http://127.0.0.1:8000` (Swagger docs available at `http://127.0.0.1:8000/docs`).

### 3. Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🔒 Configuration

Copy the sample environment file in `backend`:
```bash
cp backend/.env.example backend/.env
```
*(Optional)* Add a `GEMINI_API_KEY` in `backend/.env` if using cloud LLM features.

---

## 📄 License
MIT License.
