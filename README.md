# Japanese Text Analysis System

An advanced web application for Japanese language learning and analysis. Upload images or input text to get OCR extraction, morphological analysis, dictionary lookups, and interactive furigana rendering.

## Preview

![Application Preview 1](preview1.png)

![Application Preview 2](preview2.png)

## Features

- **OCR Processing**: Extract text from images with confidence scoring
- **Multi-model Tokenization**: Uses 4 Japanese tokenizers with consensus algorithm
- **Dictionary Lookups**: 212,380+ entries with detailed definitions
- **Furigana Rendering**: Automatic reading overlays for kanji
- **Grammar Analysis**: 50+ Japanese grammar patterns detection
- **Interactive UI**: Click tokens for definitions and grammar explanations

## Quick Start

### Prerequisites

- **Node.js** (v16 or higher)
- **Python** (3.8 or higher)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd JPLT
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   npm install
   ```

3. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Set up Python services**
   ```bash
   # Parser service
   cd ../backend/parser_service
   python -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate          # Linux/Mac
   # OR
   venv\Scripts\activate            # Windows
   
   pip install -r requirements.txt
   
   # OCR service
   cd ../ocr_service
   pip install -r requirements.txt
   ```

### Running the Application

Start all services in separate terminals:

1. **Parser Service** (Terminal 1)
   ```bash
   cd backend/parser_service
   source venv/bin/activate         # Linux/Mac
   # OR venv\Scripts\activate       # Windows
   uvicorn parser:app --host 0.0.0.0 --port 8001
   ```

2. **OCR Service** (Terminal 2)
   ```bash
   cd backend/ocr_service
   uvicorn ocr_server:app --host 0.0.0.0 --port 8000
   ```

3. **Backend API** (Terminal 3)
   ```bash
   cd backend
   node server.js
   ```

4. **Frontend** (Terminal 4)
   ```bash
   cd frontend
   npm run dev
   ```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3000
- **Parser Service**: http://localhost:8001
- **OCR Service**: http://localhost:8000

## Usage

1. **Upload an image** or **paste Japanese text** into the input area
2. **Click "Analyze"** to process the text
3. **View results** with furigana overlays and grammar highlighting
4. **Click any token** to see detailed definitions and grammar information

## Architecture

```
Frontend (Vue.js) ↔ Backend API (Express) ↔ Parser Service (FastAPI)
                           ↓
                    Dictionary System (SQLite)
                           ↓
                    OCR Service (FastAPI)
```

## Key Components

- **Multi-model Consensus**: GiNZA, Sudachi A/B/C, Fugashi tokenizers
- **Grammar Engine**: 50+ pattern database with LRU caching
- **Dictionary System**: JMdict with 212,380+ entries
- **OCR Processing**: Tesseract with Japanese language support

## Testing

```bash
# Test parser service
cd backend/parser_service
python -m pytest tests/ -v

# Test individual services
curl http://localhost:8001/health  # Parser
curl http://localhost:8000/health  # OCR
curl http://localhost:3000/health  # Backend
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in service configuration files
2. **Python dependencies**: Ensure virtual environment is activated
3. **Node modules**: Delete `node_modules` and run `npm install` again
4. **Database issues**: Check that `dictionary.sqlite` exists in backend folder

### Windows Users

- Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- Some native modules may need rebuilding: `npm rebuild`

## Development

The project uses:
- **Frontend**: Vue.js 3 + Vite + Tailwind CSS
- **Backend**: Node.js + Express + SQLite
- **NLP**: Python + FastAPI + spaCy + GiNZA
- **OCR**: Tesseract + Python

## License

MIT License

Copyright (c) 2025 Shan Li Chin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.