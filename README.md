# AI Answer System

Minimal starter structure for an AI/NLP demo app.

## Quick Start

1. **Install backend dependencies:**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend\requirements.txt
   ```

2. **Run the Flask backend:**
   ```cmd
   set FLASK_ENV=development
   python backend\app.py
   ```

3. **Open the frontend:**
   Open `frontend\index.html` in your browser

## Notes

Replace the `nlp_processor` with real NLP logic (spaCy, transformers) when ready.
