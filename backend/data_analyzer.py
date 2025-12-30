"""
Data Analyzer - Direct LLM-based data analysis
NO CrewAI - just fast, direct queries with context.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import json
from langchain_openai import ChatOpenAI
from df_context import get_dataframe_context


def analyze_data(df: pd.DataFrame, query: str) -> str:
    """
    Analyze data directly using LLM with full dataframe context.
    Much faster than CrewAI agents - no agent loops.
    """
    # Get dataframe context
    df_context = get_dataframe_context(df)
    
    # Quick stats that can be computed directly
    quick_stats = _compute_quick_stats(df, query)
    if quick_stats:
        return quick_stats
    
    # For complex queries, use LLM
    return _llm_analyze(df, query, df_context)


def _compute_quick_stats(df: pd.DataFrame, query: str) -> str | None:
    """
    Compute common statistics directly without LLM.
    Fast path for common queries.
    """
    query_lower = query.lower()
    
    try:
        # Null value queries
        if "null" in query_lower or "missing" in query_lower:
            null_counts = df.isnull().sum()
            null_pct = (null_counts / len(df) * 100).round(1)
            
            if "30%" in query or "30 %" in query:
                high_null = null_pct[null_pct > 30]
                if len(high_null) == 0:
                    return "No features have more than 30% null values."
                result = f"**{len(high_null)} features** have more than 30% null values:\n\n"
                for col, pct in high_null.items():
                    result += f"- {col}: {pct}% missing\n"
                return result
            
            # General null query
            result = "**Null value summary:**\n\n"
            for col, pct in null_pct[null_pct > 0].items():
                result += f"- {col}: {pct}% ({null_counts[col]} values)\n"
            if null_pct.sum() == 0:
                result = "No missing values in the dataset."
            return result
        
        # Row/column count
        if "how many row" in query_lower:
            return f"The dataset has **{len(df):,} rows**."
        
        if "how many column" in query_lower or "how many feature" in query_lower:
            return f"The dataset has **{len(df.columns)} columns/features**."
        
        # Column listing
        if "list" in query_lower and "column" in query_lower:
            return "**Columns:** " + ", ".join(df.columns.tolist())
        
        # Data types
        if "data type" in query_lower or "dtype" in query_lower:
            result = "**Data types:**\n\n"
            for col, dtype in df.dtypes.items():
                result += f"- {col}: {dtype}\n"
            return result
        
        # Mean/average
        if "mean" in query_lower or "average" in query_lower:
            num_cols = df.select_dtypes(include=['number']).columns
            for col in num_cols:
                if col.lower() in query_lower:
                    mean_val = df[col].mean()
                    return f"The mean of **{col}** is **{mean_val:.2f}**"
            # All means
            result = "**Mean values:**\n\n"
            for col in num_cols:
                result += f"- {col}: {df[col].mean():.2f}\n"
            return result
        
        # Unique values
        if "unique" in query_lower:
            result = "**Unique value counts:**\n\n"
            for col in df.columns:
                if col.lower() in query_lower:
                    return f"**{col}** has **{df[col].nunique()}** unique values: {', '.join(str(v) for v in df[col].unique()[:10])}"
            for col in df.columns:
                result += f"- {col}: {df[col].nunique()}\n"
            return result
        
        # Value counts for specific column
        if "value count" in query_lower or "distribution" in query_lower:
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            for col in cat_cols:
                if col.lower() in query_lower:
                    counts = df[col].value_counts()
                    result = f"**{col} distribution:**\n\n"
                    for val, cnt in counts.items():
                        pct = cnt / len(df) * 100
                        result += f"- {val}: {cnt} ({pct:.1f}%)\n"
                    return result
        
        return None  # No quick stats available, use LLM
        
    except Exception as e:
        return None


def _llm_analyze(df: pd.DataFrame, query: str, df_context: str) -> str:
    """Use LLM for complex analysis queries."""
    
    # Prepare sample data for context
    sample_data = df.head(5).to_string()
    
    prompt = f"""You are a data analyst. Answer the following question about the dataset.

QUESTION: {query}

{df_context}

SAMPLE DATA (first 5 rows):
{sample_data}

RULES:
1. Give a SHORT, DIRECT answer in 1-3 sentences
2. Include specific numbers when relevant
3. Use markdown formatting (bold for key numbers)
4. NO recommendations, insights sections, or verbose explanations
5. Just answer the question"""

    try:
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Error analyzing data: {str(e)}"


def compute_statistics(df: pd.DataFrame, query: str) -> str:
    """Compute statistical measures."""
    query_lower = query.lower()
    num_cols = df.select_dtypes(include=['number']).columns
    
    # Find relevant column
    target_col = None
    for col in num_cols:
        if col.lower() in query_lower:
            target_col = col
            break
    
    if target_col is None and len(num_cols) > 0:
        target_col = num_cols[0]
    
    if target_col is None:
        return "No numeric columns found for statistical analysis."
    
    # Compute stats
    series = df[target_col].dropna()
    stats = {
        "mean": series.mean(),
        "median": series.median(),
        "std": series.std(),
        "min": series.min(),
        "max": series.max(),
        "count": len(series)
    }
    
    result = f"**Statistics for {target_col}:**\n\n"
    result += f"- Mean: {stats['mean']:.2f}\n"
    result += f"- Median: {stats['median']:.2f}\n"
    result += f"- Std Dev: {stats['std']:.2f}\n"
    result += f"- Range: {stats['min']:.2f} to {stats['max']:.2f}\n"
    result += f"- Count: {stats['count']:,}\n"
    
    return result
