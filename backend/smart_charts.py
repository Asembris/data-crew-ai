"""
Smart Chart Generator
Uses LLM with dataframe context and styling to generate accurate Plotly charts.
Based on the blog post architecture of providing data context to the agent.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import json
from langchain_openai import ChatOpenAI
from df_context import get_dataframe_context, suggest_columns, get_categorical_columns, get_numeric_columns
from styling_guide import get_styling_instructions, get_chart_template

# LangSmith tracing
from langchain_core.tracers import LangChainTracer
from langchain_core.callbacks import CallbackManager


def get_callbacks():
    """Get LangSmith callbacks if enabled."""
    if os.getenv("LANGSMITH_TRACING", "").lower() == "true":
        tracer = LangChainTracer(project_name=os.getenv("LANGSMITH_PROJECT", "crew-analysis"))
        return CallbackManager([tracer])
    return None


def generate_chart_with_llm(df: pd.DataFrame, query: str, chart_type: str) -> str:
    """
    Generate a Plotly chart using LLM with full dataframe context.
    This approach gives the LLM complete knowledge of available columns.
    """
    # Get dataframe context
    df_context = get_dataframe_context(df)
    
    # Get styling instructions
    styling = get_styling_instructions(chart_type)
    
    # Get chart template
    template = get_chart_template(chart_type)
    
    # Suggest relevant columns
    suggested_cols = suggest_columns(df, query)
    
    # Build the prompt
    prompt = f"""You are a Plotly data visualization expert. Generate a valid Plotly JSON configuration.

USER REQUEST: {query}

CHART TYPE: {chart_type}

{df_context}

SUGGESTED COLUMNS TO USE: {', '.join(suggested_cols)}

{styling}

TEMPLATE STRUCTURE:
{template}

INSTRUCTIONS:
1. ONLY use column names that exist in the AVAILABLE COLUMNS section above
2. Use the data to create realistic values (you can estimate based on the column info)
3. Follow the styling guidelines
4. Return ONLY valid JSON, no markdown, no explanation
5. The JSON must have "data" (array) and "layout" (object) keys

If a column mentioned in the request doesn't exist, use the closest matching column from AVAILABLE COLUMNS.

IMPORTANT: Return ONLY the Plotly JSON object, nothing else."""

    try:
        callbacks = get_callbacks()
        llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.1,
            callbacks=callbacks.handlers if callbacks else None
        )
        
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Clean response
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0]
        elif '```' in content:
            content = content.split('```')[1].split('```')[0]
        
        # Validate JSON
        parsed = json.loads(content)
        if 'data' not in parsed:
            raise ValueError("Missing 'data' key in response")
        
        return content
        
    except Exception as e:
        print(f"LLM chart generation failed: {e}")
        # Fallback to direct chart generation
        return generate_fallback_chart(df, query, chart_type)


def generate_fallback_chart(df: pd.DataFrame, query: str, chart_type: str) -> str:
    """Direct chart generation as fallback when LLM fails."""
    cat_cols = get_categorical_columns(df)
    num_cols = get_numeric_columns(df)
    
    if chart_type in ["bar", "horizontal_bar"]:
        col = cat_cols[0] if cat_cols else df.columns[0]
        counts = df[col].value_counts().head(8)
        
        if chart_type == "horizontal_bar":
            return json.dumps({
                "data": [{
                    "x": counts.values.tolist(),
                    "y": counts.index.astype(str).tolist(),
                    "type": "bar",
                    "orientation": "h",
                    "marker": {"color": "#8b5cf6"}
                }],
                "layout": {
                    "title": f"Distribution of {col}",
                    "xaxis": {"title": "Count"},
                    "yaxis": {"title": col}
                }
            })
        else:
            return json.dumps({
                "data": [{
                    "x": counts.index.astype(str).tolist(),
                    "y": counts.values.tolist(),
                    "type": "bar",
                    "marker": {"color": "#8b5cf6"}
                }],
                "layout": {
                    "title": f"Count of {col}",
                    "xaxis": {"title": col},
                    "yaxis": {"title": "Count"}
                }
            })
    
    elif chart_type == "grouped_bar":
        if len(cat_cols) >= 2:
            col1, col2 = cat_cols[0], cat_cols[1]
            grouped = df.groupby([col1, col2]).size().unstack(fill_value=0)
            colors = ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444"]
            traces = []
            for i, c in enumerate(grouped.columns[:5]):
                traces.append({
                    "x": grouped.index.astype(str).tolist(),
                    "y": grouped[c].tolist(),
                    "type": "bar",
                    "name": str(c),
                    "marker": {"color": colors[i % len(colors)]}
                })
            return json.dumps({
                "data": traces,
                "layout": {
                    "title": f"{col2} by {col1}",
                    "barmode": "group",
                    "showlegend": True
                }
            })
        else:
            return generate_fallback_chart(df, query, "bar")
    
    elif chart_type == "scatter":
        if len(num_cols) >= 2:
            x_col, y_col = num_cols[0], num_cols[1]
            sample = df[[x_col, y_col]].dropna().head(500)
            return json.dumps({
                "data": [{
                    "x": sample[x_col].tolist(),
                    "y": sample[y_col].tolist(),
                    "type": "scatter",
                    "mode": "markers",
                    "marker": {"color": "#8b5cf6", "opacity": 0.7}
                }],
                "layout": {
                    "title": f"{y_col} vs {x_col}",
                    "xaxis": {"title": x_col},
                    "yaxis": {"title": y_col}
                }
            })
        else:
            return generate_fallback_chart(df, query, "bar")
    
    elif chart_type == "histogram":
        col = num_cols[0] if num_cols else df.columns[0]
        return json.dumps({
            "data": [{
                "x": df[col].dropna().head(1000).tolist(),
                "type": "histogram",
                "marker": {"color": "#8b5cf6"}
            }],
            "layout": {
                "title": f"Distribution of {col}",
                "xaxis": {"title": col},
                "yaxis": {"title": "Frequency"}
            }
        })
    
    elif chart_type == "pie":
        col = cat_cols[0] if cat_cols else df.columns[0]
        counts = df[col].value_counts().head(6)
        return json.dumps({
            "data": [{
                "labels": counts.index.astype(str).tolist(),
                "values": counts.values.tolist(),
                "type": "pie",
                "hole": 0.4
            }],
            "layout": {"title": f"{col} Distribution"}
        })
    
    elif chart_type == "heatmap":
        if len(num_cols) >= 2:
            corr = df[num_cols].corr().round(2)
            return json.dumps({
                "data": [{
                    "z": corr.values.tolist(),
                    "x": corr.columns.tolist(),
                    "y": corr.columns.tolist(),
                    "type": "heatmap",
                    "colorscale": "RdBu",
                    "zmid": 0
                }],
                "layout": {"title": "Correlation Matrix"}
            })
        else:
            return generate_fallback_chart(df, query, "bar")
    
    else:
        # Default bar chart
        col = cat_cols[0] if cat_cols else df.columns[0]
        counts = df[col].value_counts().head(8)
        return json.dumps({
            "data": [{
                "x": counts.index.astype(str).tolist(),
                "y": counts.values.tolist(),
                "type": "bar",
                "marker": {"color": "#8b5cf6"}
            }],
            "layout": {"title": f"Count of {col}"}
        })
