"""
Direct Chart Generator with Plotly Templates
Generates charts based on semantic chart type classification.
"""
import pandas as pd
import numpy as np
import json
from typing import Optional, List


def generate_chart(df: pd.DataFrame, query: str, chart_type: str, columns: List[str] = None) -> str:
    """
    Generate a Plotly chart based on the classified chart type.
    
    Args:
        df: The DataFrame
        query: Original user query
        chart_type: Classified chart type (scatter, bar, histogram, etc.)
        columns: Detected column names from query
    """
    # Find columns mentioned in query
    if not columns:
        columns = _find_columns(df, query)
    
    generators = {
        "scatter": _scatter_plot,
        "line": _line_chart,
        "histogram": _histogram,
        "bar": _bar_chart,
        "horizontal_bar": _horizontal_bar,
        "grouped_bar": _grouped_bar,
        "pie": _pie_chart,
        "heatmap": _heatmap,
        "box": _box_plot,
    }
    
    generator = generators.get(chart_type, _bar_chart)
    
    try:
        result = generator(df, query, columns)
        return result
    except KeyError as e:
        # Column not found - return helpful error chart
        return _error_chart(f"Column not found: {e}. Available columns: {', '.join(df.columns[:5])}...")
    except Exception as e:
        # Fallback to simple bar or error message
        try:
            return _bar_chart(df, query, columns)
        except:
            return _error_chart(f"Chart error: {str(e)}")


def _find_columns(df: pd.DataFrame, query: str) -> List[str]:
    """Find column names mentioned in the query."""
    query_lower = query.lower()
    found = []
    for col in df.columns:
        if col.lower() in query_lower:
            found.append(col)
    return found


def _get_numeric_cols(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=['number']).columns.tolist()


def _get_categorical_cols(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


# ============== CHART GENERATORS ==============

def _scatter_plot(df: pd.DataFrame, query: str, columns: List[str]) -> str:
    """Scatter plot for relationship between two variables."""
    num_cols = _get_numeric_cols(df)
    
    # Get two numeric columns
    if len(columns) >= 2:
        x_col = columns[0] if columns[0] in num_cols else num_cols[0]
        y_col = columns[1] if columns[1] in num_cols else num_cols[1] if len(num_cols) > 1 else num_cols[0]
    elif len(num_cols) >= 2:
        x_col, y_col = num_cols[0], num_cols[1]
    else:
        x_col = y_col = num_cols[0] if num_cols else df.columns[0]
    
    # Sample data if too large
    sample_df = df[[x_col, y_col]].dropna()
    if len(sample_df) > 1000:
        sample_df = sample_df.sample(1000)
    
    # Add trendline
    x_data = sample_df[x_col].tolist()
    y_data = sample_df[y_col].tolist()
    
    # Calculate trendline (linear regression)
    z = np.polyfit(sample_df[x_col], sample_df[y_col], 1)
    p = np.poly1d(z)
    x_trend = [min(x_data), max(x_data)]
    y_trend = [p(x) for x in x_trend]
    
    return json.dumps({
        "data": [
            {
                "x": x_data,
                "y": y_data,
                "type": "scatter",
                "mode": "markers",
                "name": "Data",
                "marker": {"color": "#8b5cf6", "size": 8, "opacity": 0.6}
            },
            {
                "x": x_trend,
                "y": y_trend,
                "type": "scatter",
                "mode": "lines",
                "name": "Trend",
                "line": {"color": "#ef4444", "width": 2, "dash": "dash"}
            }
        ],
        "layout": {
            "title": f"{y_col} vs {x_col}",
            "xaxis": {"title": x_col},
            "yaxis": {"title": y_col},
            "showlegend": True
        }
    })


def _line_chart(df: pd.DataFrame, query: str, columns: List[str]) -> str:
    """Line chart for trends over time or sequence."""
    num_cols = _get_numeric_cols(df)
    
    if columns and columns[0] in num_cols:
        y_col = columns[0]
    else:
        y_col = num_cols[0] if num_cols else df.columns[0]
    
    data = df[y_col].dropna().head(100).tolist()
    
    return json.dumps({
        "data": [{
            "y": data,
            "type": "scatter",
            "mode": "lines+markers",
            "name": y_col,
            "line": {"color": "#8b5cf6", "width": 2},
            "marker": {"size": 4}
        }],
        "layout": {
            "title": f"Trend of {y_col}",
            "xaxis": {"title": "Index"},
            "yaxis": {"title": y_col}
        }
    })


def _histogram(df: pd.DataFrame, query: str, columns: List[str]) -> str:
    """Histogram for distribution of a single variable."""
    num_cols = _get_numeric_cols(df)
    
    if columns and columns[0] in num_cols:
        col = columns[0]
    else:
        col = num_cols[0] if num_cols else df.columns[0]
    
    data = df[col].dropna().tolist()
    
    return json.dumps({
        "data": [{
            "x": data,
            "type": "histogram",
            "marker": {"color": "#8b5cf6", "line": {"color": "#fff", "width": 1}},
            "nbinsx": 30
        }],
        "layout": {
            "title": f"Distribution of {col}",
            "xaxis": {"title": col},
            "yaxis": {"title": "Frequency"},
            "bargap": 0.05
        }
    })


def _bar_chart(df: pd.DataFrame, query: str, columns: List[str]) -> str:
    """Simple bar chart for category counts."""
    cat_cols = _get_categorical_cols(df)
    
    if columns:
        col = columns[0]
    else:
        col = cat_cols[0] if cat_cols else df.columns[0]
    
    counts = df[col].value_counts().head(10)
    
    return json.dumps({
        "data": [{
            "x": counts.index.tolist(),
            "y": counts.values.tolist(),
            "type": "bar",
            "marker": {
                "color": ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", 
                          "#ec4899", "#6366f1", "#14b8a6", "#f97316", "#a855f7"][:len(counts)]
            }
        }],
        "layout": {
            "title": f"Count of {col}",
            "xaxis": {"title": col},
            "yaxis": {"title": "Count"}
        }
    })


def _horizontal_bar(df: pd.DataFrame, query: str, columns: List[str]) -> str:
    """Horizontal bar chart for category distribution."""
    cat_cols = _get_categorical_cols(df)
    
    # Find two categorical columns for comparison
    if len(columns) >= 2:
        value_col, group_col = columns[0], columns[1]
    elif len(columns) == 1 and len(cat_cols) >= 1:
        value_col = columns[0]
        group_col = [c for c in cat_cols if c != value_col][0] if len(cat_cols) > 1 else cat_cols[0]
    elif len(cat_cols) >= 2:
        value_col, group_col = cat_cols[0], cat_cols[1]
    else:
        # Fall back to simple horizontal bar
        col = columns[0] if columns else (cat_cols[0] if cat_cols else df.columns[0])
        counts = df[col].value_counts().head(10)
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
    
    # Grouped horizontal bar
    grouped = df.groupby([value_col, group_col]).size().unstack(fill_value=0)
    colors = ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#ec4899"]
    traces = []
    
    for i, col in enumerate(grouped.columns):
        traces.append({
            "x": grouped[col].tolist(),
            "y": grouped.index.astype(str).tolist(),
            "type": "bar",
            "orientation": "h",
            "name": str(col),
            "marker": {"color": colors[i % len(colors)]}
        })
    
    return json.dumps({
        "data": traces,
        "layout": {
            "title": f"{value_col} Distribution by {group_col}",
            "barmode": "group",
            "xaxis": {"title": "Count"},
            "yaxis": {"title": value_col},
            "showlegend": True
        }
    })


def _error_chart(message: str) -> str:
    """Return an error message as a text annotation chart."""
    return json.dumps({
        "data": [{
            "x": [0.5],
            "y": [0.5],
            "mode": "text",
            "text": [f"⚠️ {message}"],
            "textfont": {"size": 14, "color": "#ef4444"},
            "type": "scatter"
        }],
        "layout": {
            "title": "Chart Generation Error",
            "xaxis": {"visible": False, "range": [0, 1]},
            "yaxis": {"visible": False, "range": [0, 1]},
            "annotations": [{
                "text": message,
                "showarrow": False,
                "x": 0.5,
                "y": 0.5,
                "font": {"size": 12}
            }]
        }
    })


def _grouped_bar(df: pd.DataFrame, query: str, columns: List[str]) -> str:
    """Grouped bar chart for comparing categories across groups."""
    cat_cols = _get_categorical_cols(df)
    
    if len(columns) >= 2:
        value_col, group_col = columns[0], columns[1]
    elif len(cat_cols) >= 2:
        value_col, group_col = cat_cols[0], cat_cols[1]
    else:
        return _bar_chart(df, query, columns)
    
    grouped = df.groupby([group_col, value_col]).size().unstack(fill_value=0)
    
    colors = ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#ec4899"]
    traces = []
    
    for i, col in enumerate(grouped.columns):
        traces.append({
            "x": grouped.index.tolist(),
            "y": grouped[col].tolist(),
            "type": "bar",
            "name": str(col),
            "marker": {"color": colors[i % len(colors)]}
        })
    
    return json.dumps({
        "data": traces,
        "layout": {
            "title": f"{value_col} by {group_col}",
            "barmode": "group",
            "xaxis": {"title": group_col},
            "yaxis": {"title": "Count"},
            "showlegend": True
        }
    })


def _pie_chart(df: pd.DataFrame, query: str, columns: List[str]) -> str:
    """Pie chart for proportions."""
    cat_cols = _get_categorical_cols(df)
    
    if columns:
        col = columns[0]
    else:
        col = cat_cols[0] if cat_cols else df.columns[0]
    
    counts = df[col].value_counts().head(8)
    
    return json.dumps({
        "data": [{
            "labels": counts.index.tolist(),
            "values": counts.values.tolist(),
            "type": "pie",
            "hole": 0.4,
            "marker": {
                "colors": ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", 
                           "#ef4444", "#ec4899", "#6366f1", "#14b8a6"]
            }
        }],
        "layout": {
            "title": f"{col} Distribution"
        }
    })


def _heatmap(df: pd.DataFrame, query: str, columns: List[str]) -> str:
    """Correlation heatmap for numeric columns."""
    num_cols = _get_numeric_cols(df)
    
    if len(num_cols) < 2:
        return _bar_chart(df, query, columns)
    
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
        "layout": {
            "title": "Correlation Matrix"
        }
    })


def _box_plot(df: pd.DataFrame, query: str, columns: List[str]) -> str:
    """Box plot for distribution comparison."""
    num_cols = _get_numeric_cols(df)
    cat_cols = _get_categorical_cols(df)
    
    if columns:
        y_col = columns[0] if columns[0] in num_cols else num_cols[0]
        x_col = columns[1] if len(columns) > 1 and columns[1] in cat_cols else (cat_cols[0] if cat_cols else None)
    else:
        y_col = num_cols[0] if num_cols else df.columns[0]
        x_col = cat_cols[0] if cat_cols else None
    
    if x_col:
        traces = []
        colors = ["#8b5cf6", "#3b82f6", "#10b981", "#f59e0b", "#ef4444"]
        for i, cat in enumerate(df[x_col].unique()[:5]):
            traces.append({
                "y": df[df[x_col] == cat][y_col].tolist(),
                "type": "box",
                "name": str(cat),
                "marker": {"color": colors[i % len(colors)]}
            })
        data = traces
    else:
        data = [{"y": df[y_col].tolist(), "type": "box", "marker": {"color": "#8b5cf6"}}]
    
    return json.dumps({
        "data": data,
        "layout": {
            "title": f"Distribution of {y_col}" + (f" by {x_col}" if x_col else ""),
            "yaxis": {"title": y_col}
        }
    })


# Legacy function for backwards compatibility
def generate_direct_chart(df: pd.DataFrame, query: str) -> Optional[str]:
    """Legacy wrapper - auto-detect chart type."""
    query_lower = query.lower()
    
    # Inline chart type detection to avoid circular import
    if "scatter" in query_lower or any(kw in query_lower for kw in ["relationship", "vs", "between", "dependence"]):
        chart_type = "scatter"
    elif "pie" in query_lower or "proportion" in query_lower:
        chart_type = "pie"
    elif "histogram" in query_lower or "distribution of" in query_lower:
        chart_type = "histogram"
    elif "heatmap" in query_lower or "correlation matrix" in query_lower:
        chart_type = "heatmap"
    elif "box" in query_lower:
        chart_type = "box"
    elif "line" in query_lower or "trend" in query_lower:
        chart_type = "line"
    elif "by" in query_lower or "within" in query_lower:
        chart_type = "grouped_bar"
    else:
        chart_type = "bar"
    
    return generate_chart(df, query, chart_type)
