# Architecture Deep Dive

## Overview

Data Crew AI uses a **direct LLM architecture** - no agents, no loops, just fast query processing.

---

## Query Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                 │
│  POST /chat                                                     │
│    │                                                            │
│    ├── router.classify_query(query)                             │
│    │   └── Returns: (query_type, chart_type)                    │
│    │                                                            │
│    ├── if visualizer:                                           │
│    │   └── smart_charts.generate_chart_with_llm(df, query)      │
│    │       ├── df_context.get_dataframe_context(df)             │
│    │       ├── styling_guide.get_styling_instructions()         │
│    │       └── LLM generates Plotly JSON                        │
│    │                                                            │
│    └── else:                                                    │
│        └── data_analyzer.analyze_data(df, query)                │
│            ├── Quick stats (pandas) OR                          │
│            └── LLM with context                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Responsibilities

### `router.py`
**Purpose**: Fast query classification without LLM

```python
def classify_query(query: str) -> tuple:
    # Keyword matching - instant, no API call
    if "chart" in query or "plot" in query:
        return 'visualizer', detect_chart_type(query)
    return 'analyst', None
```

### `data_analyzer.py`
**Purpose**: Handle text queries

1. **Quick Stats Path** (instant):
   - Null value counts
   - Row/column counts
   - Mean/median calculations
   - Value counts

2. **LLM Path** (for complex questions):
   - Full df.info() context
   - Sample data provided
   - Concise response formatting

### `smart_charts.py`  
**Purpose**: Generate Plotly charts via LLM

1. Get dataframe context (column names, types, ranges)
2. Get styling instructions for chart type
3. LLM generates Plotly JSON
4. Fallback to direct generation if LLM fails

### `df_context.py`
**Purpose**: Create structured context for LLM

```python
def get_dataframe_context(df) -> str:
    # Returns formatted string:
    # DATASET INFO:
    # - Total rows: 891
    # - Total columns: 12
    #
    # AVAILABLE COLUMNS:
    # • PassengerId:
    #   Type: numeric
    #   Range: 1 to 891
```

---

## Why Not Agents?

We tried CrewAI agents initially. Problems:
1. **Slow** - Multiple LLM calls per query
2. **Unreliable** - Agents would get stuck in loops
3. **Overkill** - Data analysis doesn't need agent reasoning

Direct LLM calls are:
- 5-10x faster
- More predictable
- Easier to debug

---

## Chart Generation Strategy

1. **LLM with Context** (primary)
   - LLM sees all column names
   - Can't hallucinate non-existent columns
   - Follows styling guidelines

2. **Direct Generation** (fallback)
   - If LLM fails, use pandas + plotly directly
   - Always returns valid chart

3. **Ultimate Fallback**
   - Simple bar chart of first categorical column
   - Never returns empty/error

---

## LangSmith Integration

Set environment variables:
```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=crew-analysis
LANGSMITH_API_KEY=your-key
```

All `ChatOpenAI` calls are automatically traced.
