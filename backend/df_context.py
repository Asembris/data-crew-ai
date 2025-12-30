"""
DataFrame Context Provider
Provides structured information about the dataset to help the visualization agent.
Based on the blog post approach of indexing dataframe metadata.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List


def get_dataframe_context(df: pd.DataFrame) -> str:
    """
    Generate a structured context string about the dataframe.
    This gives the agent complete knowledge of available columns and their characteristics.
    """
    context_parts = []
    
    # Dataset overview
    context_parts.append(f"DATASET INFO:")
    context_parts.append(f"- Total rows: {len(df)}")
    context_parts.append(f"- Total columns: {len(df.columns)}")
    context_parts.append("")
    
    # Column details
    context_parts.append("AVAILABLE COLUMNS:")
    
    for col in df.columns:
        col_info = _get_column_info(df, col)
        context_parts.append(f"\n• {col}:")
        context_parts.append(f"  Type: {col_info['type']}")
        context_parts.append(f"  Non-null: {col_info['non_null_count']}/{len(df)}")
        
        if col_info['type'] == 'numeric':
            context_parts.append(f"  Range: {col_info['min']} to {col_info['max']}")
            context_parts.append(f"  Mean: {col_info['mean']:.2f}")
        elif col_info['type'] == 'categorical':
            context_parts.append(f"  Unique values: {col_info['unique_count']}")
            context_parts.append(f"  Top values: {', '.join(str(v) for v in col_info['top_values'])}")
        elif col_info['type'] == 'datetime':
            context_parts.append(f"  Date range: {col_info['min']} to {col_info['max']}")
    
    return "\n".join(context_parts)


def _get_column_info(df: pd.DataFrame, col: str) -> Dict[str, Any]:
    """Get detailed info about a single column."""
    series = df[col]
    non_null = series.dropna()
    
    info = {
        'name': col,
        'non_null_count': len(non_null),
    }
    
    # Determine type and get relevant stats
    if pd.api.types.is_numeric_dtype(series):
        info['type'] = 'numeric'
        if len(non_null) > 0:
            info['min'] = float(non_null.min())
            info['max'] = float(non_null.max())
            info['mean'] = float(non_null.mean())
        else:
            info['min'] = info['max'] = info['mean'] = 0
            
    elif pd.api.types.is_datetime64_any_dtype(series):
        info['type'] = 'datetime'
        if len(non_null) > 0:
            info['min'] = str(non_null.min())
            info['max'] = str(non_null.max())
        else:
            info['min'] = info['max'] = 'N/A'
            
    else:
        info['type'] = 'categorical'
        info['unique_count'] = series.nunique()
        info['top_values'] = series.value_counts().head(5).index.tolist()
    
    return info


def get_column_names(df: pd.DataFrame) -> List[str]:
    """Get list of all column names."""
    return df.columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """Get list of categorical column names."""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Get list of numeric column names."""
    return df.select_dtypes(include=['number']).columns.tolist()


def validate_columns(df: pd.DataFrame, columns: List[str]) -> tuple:
    """
    Validate that columns exist in the dataframe.
    Returns (valid_columns, invalid_columns)
    """
    valid = [c for c in columns if c in df.columns]
    invalid = [c for c in columns if c not in df.columns]
    return valid, invalid


def suggest_columns(df: pd.DataFrame, query: str) -> List[str]:
    """
    Suggest relevant columns based on the query.
    Uses fuzzy matching on column names.
    """
    query_words = query.lower().split()
    suggestions = []
    
    for col in df.columns:
        col_lower = col.lower()
        for word in query_words:
            if word in col_lower or col_lower in word:
                suggestions.append(col)
                break
    
    # If no matches, return first few categorical + numeric columns
    if not suggestions:
        cat_cols = get_categorical_columns(df)[:2]
        num_cols = get_numeric_columns(df)[:2]
        suggestions = cat_cols + num_cols
    
    return suggestions
