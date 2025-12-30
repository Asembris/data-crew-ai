# Data Crew AI 🤖

AI-powered data analysis with **instant insights** and **interactive visualizations**.

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![GPT-4o](https://img.shields.io/badge/GPT--4o--mini-412991?logo=openai&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)

---

## ⚡ Try It

```bash
# Upload a file
curl -X POST http://localhost:8000/upload -F "file=@data.csv"

# Ask a question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "show distribution of Age"}'
```

---

## 🏗️ Architecture

```
User Query → Keyword Router → Data Analyzer / Chart Generator → Response
                  │                    │
                  │              ┌─────┴─────┐
                  │              │           │
             (instant)      Quick Stats   LLM+Context
                            (pandas)     (GPT-4o-mini)
```

**No agents. No loops. Just fast, direct queries.**

---

## 📊 How It Works

1. **Upload** → Parse CSV with pandas, validate structure
2. **Query** → Router classifies intent using keywords (no LLM overhead)
3. **Process**:
   - **Stats queries** → Direct pandas computation (instant)
   - **Charts** → LLM generates Plotly JSON with full column context
   - **Analysis** → LLM with df.info() context for complex questions
4. **Render** → JSON response to React frontend

---

## 💬 Example Queries

| Query | Type | Speed |
|-------|------|-------|
| "How many rows?" | Stats | ⚡ <100ms |
| "Show missing values" | Stats | ⚡ <100ms |
| "Bar chart of Sex" | Chart | 🚀 2-3s |
| "Scatter Age vs Fare" | Chart | 🚀 2-3s |
| "What's the mean Age?" | Stats | ⚡ <100ms |

---

## ⚠️ Limitations

| Limit | Value |
|-------|-------|
| Max file size | 50 MB |
| Max columns | 500 |
| Supported formats | CSV only |
| Rate limit | 100 req/min |

---

## 🔒 Security

- **No code execution** — LLM generates JSON configs, not executable code
- **Input sanitization** — All queries validated before processing  
- **In-memory only** — Uploaded files processed in RAM, not persisted
- **No external calls** — Data never leaves your server (except OpenAI API)

---

## 🚀 Quick Start

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate      # Windows
source .venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Create `.env`:
```env
OPENAI_API_KEY=sk-your-key

# Optional: LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=crew-analysis
LANGSMITH_API_KEY=your-key
```

Run:
```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

---

## 🐳 Docker

```bash
docker-compose up
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

---

## 📁 Project Structure

```
backend/
├── main.py           # FastAPI endpoints
├── router.py         # Keyword-based query classification
├── data_analyzer.py  # Quick stats + LLM analysis
├── smart_charts.py   # LLM chart generation
├── df_context.py     # DataFrame metadata
└── styling_guide.py  # Plotly styling

frontend/
└── app/page.tsx      # React chat UI
```

---

## 📦 Dependencies

**Backend**: fastapi, uvicorn, pandas, numpy, langchain-openai, python-dotenv  
**Frontend**: next, react, react-plotly.js, framer-motion, axios

---

## 🔗 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload CSV file |
| `/chat` | POST | Send query, get response |
| `/columns` | GET | List available columns |
| `/` | GET | Health check |

---

## 📄 License

MIT
