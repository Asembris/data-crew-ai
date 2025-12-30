"""
Simple Query Router
Classifies queries without LLM for speed. LangSmith tracing added.
"""
import os


def classify_query(query: str) -> tuple:
    """
    Classify query type using keyword matching (fast, no LLM).
    Returns (query_type, chart_type)
    """
    query_lower = query.lower()
    
    # Visualization queries
    viz_keywords = ['chart', 'plot', 'graph', 'bar', 'pie', 'histogram', 
                    'scatter', 'visualiz', 'show', 'display', 'heatmap', 'box']
    
    if any(kw in query_lower for kw in viz_keywords):
        chart_type = _detect_chart_type(query_lower)
        return 'visualizer', chart_type
    
    # Everything else is analysis
    return 'analyst', None


def _detect_chart_type(query: str) -> str:
    """Detect chart type from query."""
    if "scatter" in query or "relationship" in query or " vs " in query:
        return "scatter"
    elif "horizontal" in query:
        return "horizontal_bar"
    elif "pie" in query or "proportion" in query:
        return "pie"
    elif "histogram" in query:
        return "histogram"
    elif "heatmap" in query or "correlation matrix" in query:
        return "heatmap"
    elif "box" in query:
        return "box"
    elif "line" in query and ("trend" in query or "time" in query):
        return "line"
    elif " by " in query or "across" in query or "within" in query:
        return "grouped_bar"
    else:
        return "bar"
