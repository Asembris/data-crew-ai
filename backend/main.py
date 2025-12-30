"""
Data Crew AI - Main API
Version 3.0 - Simplified architecture with no CrewAI
"""
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import pandas as pd
from pydantic import BaseModel
import uuid
import json
import traceback

# LangSmith setup
os.environ.setdefault("LANGCHAIN_TRACING_V2", os.getenv("LANGSMITH_TRACING", "false"))
os.environ.setdefault("LANGCHAIN_PROJECT", os.getenv("LANGSMITH_PROJECT", "crew-analysis"))

app = FastAPI(title="Data Crew AI", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
CHARTS_DIR = "uploads/charts"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

app.mount("/charts", StaticFiles(directory=CHARTS_DIR), name="charts")

SESSION_DATA = {}


class ChatRequest(BaseModel):
    query: str


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV and initialize session."""
    if not file.filename.endswith('.csv'):
        return {"error": "Only CSV files allowed."}
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"error": f"Failed to parse CSV: {str(e)}"}
    
    SESSION_DATA["latest"] = {"file_path": file_path, "df": df, "filename": file.filename}
    
    try:
        from profiler import profile_dataset
        profile = profile_dataset(df)
    except Exception:
        profile = {"kpis": [], "insights": []}
    
    return {"message": "File uploaded", "file_id": file_id, "profile": profile}


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with the data.
    Uses direct analysis - NO CrewAI agents - fast and reliable.
    """
    if "latest" not in SESSION_DATA:
        return {"response": "Please upload a CSV file first.", "type": "text"}
    
    df = SESSION_DATA["latest"]["df"]
    query = request.query
    
    try:
        # Classify query
        from router import classify_query
        query_type, chart_type = classify_query(query)
        
        if query_type == 'visualizer':
            # Generate chart
            result = _generate_chart(df, query, chart_type)
            return {"response": result, "type": "chart", "chart_type": chart_type}
        else:
            # Analyze data
            result = _analyze(df, query)
            return {"response": result, "type": "text"}
            
    except Exception as e:
        traceback.print_exc()
        return {"response": f"Error: {str(e)}", "type": "text"}


def _generate_chart(df: pd.DataFrame, query: str, chart_type: str) -> str:
    """Generate chart with fallback."""
    try:
        from smart_charts import generate_chart_with_llm, generate_fallback_chart
        result = generate_chart_with_llm(df, query, chart_type)
        json.loads(result)  # Validate
        return result
    except Exception as e:
        print(f"Chart error: {e}")
        try:
            from smart_charts import generate_fallback_chart
            return generate_fallback_chart(df, query, chart_type)
        except:
            # Ultimate fallback
            return _simple_bar_chart(df)


def _analyze(df: pd.DataFrame, query: str) -> str:
    """Analyze data directly - no agents."""
    try:
        from data_analyzer import analyze_data
        return analyze_data(df, query)
    except Exception as e:
        print(f"Analysis error: {e}")
        return f"Error analyzing data: {str(e)}"


def _simple_bar_chart(df: pd.DataFrame) -> str:
    """Ultimate fallback chart."""
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(cat_cols) > 0:
        counts = df[cat_cols[0]].value_counts().head(5)
        return json.dumps({
            "data": [{"x": counts.index.tolist(), "y": counts.values.tolist(), "type": "bar"}],
            "layout": {"title": cat_cols[0]}
        })
    return json.dumps({"data": [], "layout": {"title": "No data"}})


@app.get("/")
def health():
    return {"status": "running", "version": "3.0", "mode": "direct-llm"}


@app.get("/columns")
def get_columns():
    """Get available columns."""
    if "latest" not in SESSION_DATA:
        return {"columns": []}
    return {"columns": SESSION_DATA["latest"]["df"].columns.tolist()}
