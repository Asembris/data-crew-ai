"""
Data Profiler Service
Generates structured insights, KPI metrics, and auto-charts from uploaded CSV.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

# Set premium dark theme for all charts
plt.style.use('dark_background')
sns.set_theme(style="darkgrid", palette="viridis")

CHARTS_DIR = Path("uploads/charts")
CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive profile of the dataset.
    Returns structured data for KPI cards and insights.
    """
    profile = {
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "columns": [],
        "kpis": [],
        "insights": [],
        "numeric_summary": {},
        "categorical_summary": {},
    }
    
    # Column information
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isna().sum()),
            "missing_pct": round(df[col].isna().sum() / len(df) * 100, 1),
            "unique": int(df[col].nunique()),
        }
        profile["columns"].append(col_info)
    
    # KPI Cards Data
    profile["kpis"] = [
        {"label": "Total Rows", "value": f"{len(df):,}", "icon": "rows"},
        {"label": "Total Columns", "value": str(len(df.columns)), "icon": "columns"},
        {"label": "Missing Values", "value": f"{df.isna().sum().sum():,}", "icon": "missing"},
        {"label": "Numeric Cols", "value": str(len(df.select_dtypes(include=[np.number]).columns)), "icon": "numeric"},
        {"label": "Categorical Cols", "value": str(len(df.select_dtypes(include=['object', 'category']).columns)), "icon": "categorical"},
        {"label": "Memory Usage", "value": f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB", "icon": "memory"},
    ]
    
    # Numeric columns summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        desc = df[numeric_cols].describe().to_dict()
        profile["numeric_summary"] = {
            col: {
                "mean": round(stats.get("mean", 0), 2),
                "std": round(stats.get("std", 0), 2),
                "min": round(stats.get("min", 0), 2),
                "max": round(stats.get("max", 0), 2),
            }
            for col, stats in desc.items()
        }
    
    # Categorical columns summary
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in categorical_cols[:3]:  # Limit to first 3
        profile["categorical_summary"][col] = df[col].value_counts().head(5).to_dict()
    
    # Auto-generated insights
    insights = []
    
    # Missing data insight
    missing_cols = [(col, info["missing_pct"]) for col, info in zip(df.columns, profile["columns"]) if info["missing_pct"] > 0]
    if missing_cols:
        worst = max(missing_cols, key=lambda x: x[1])
        insights.append(f"⚠️ Column '{worst[0]}' has {worst[1]}% missing values")
    
    # High cardinality insight
    for col_info in profile["columns"]:
        if col_info["unique"] == len(df) and col_info["dtype"] == "object":
            insights.append(f"🔑 Column '{col_info['name']}' appears to be a unique identifier")
            break
    
    # Correlation insight (if enough numeric cols)
    if len(numeric_cols) >= 2:
        try:
            corr = df[numeric_cols].corr()
            # Find highest correlation (excluding diagonal)
            np.fill_diagonal(corr.values, 0)
            max_corr_idx = np.unravel_index(np.abs(corr.values).argmax(), corr.shape)
            max_corr = corr.values[max_corr_idx]
            if abs(max_corr) > 0.5:
                col1, col2 = corr.index[max_corr_idx[0]], corr.columns[max_corr_idx[1]]
                insights.append(f"📊 Strong correlation ({max_corr:.2f}) between '{col1}' and '{col2}'")
        except:
            pass
    
    # Dataset size insight
    if len(df) > 10000:
        insights.append(f"📈 Large dataset with {len(df):,} rows")
    elif len(df) < 100:
        insights.append(f"📉 Small dataset with only {len(df)} rows")
    
    profile["insights"] = insights[:5]  # Limit to 5 insights
    
    return profile


def generate_auto_charts(df: pd.DataFrame, max_charts: int = 3) -> List[str]:
    """
    Generate automatic exploratory charts.
    Returns list of chart image paths.
    """
    chart_paths = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Chart 1: Distribution of first numeric column
    if numeric_cols:
        fig, ax = plt.subplots(figsize=(8, 5))
        col = numeric_cols[0]
        
        # Use histogram with KDE
        data = df[col].dropna()
        ax.hist(data, bins=30, alpha=0.7, color='#6366f1', edgecolor='white', linewidth=0.5)
        ax.set_xlabel(col, fontsize=12, color='white')
        ax.set_ylabel('Frequency', fontsize=12, color='white')
        ax.set_title(f'Distribution of {col}', fontsize=14, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        
        # Style
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#444')
        ax.spines['bottom'].set_color('#444')
        fig.patch.set_facecolor('#0a0a0a')
        ax.set_facecolor('#0a0a0a')
        
        path = save_chart(fig, "distribution")
        chart_paths.append(path)
        plt.close(fig)
    
    # Chart 2: Categorical value counts (if available)
    if categorical_cols:
        col = categorical_cols[0]
        value_counts = df[col].value_counts().head(8)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(value_counts)))
        bars = ax.barh(value_counts.index.astype(str), value_counts.values, color=colors, edgecolor='white', linewidth=0.5)
        ax.set_xlabel('Count', fontsize=12, color='white')
        ax.set_title(f'Top Categories in {col}', fontsize=14, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        ax.invert_yaxis()
        
        # Add value labels
        for bar, val in zip(bars, value_counts.values):
            ax.text(val + max(value_counts) * 0.02, bar.get_y() + bar.get_height()/2, 
                   f'{val:,}', va='center', ha='left', fontsize=10, color='white')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#444')
        ax.spines['bottom'].set_color('#444')
        fig.patch.set_facecolor('#0a0a0a')
        ax.set_facecolor('#0a0a0a')
        
        path = save_chart(fig, "categories")
        chart_paths.append(path)
        plt.close(fig)
    
    # Chart 3: Correlation heatmap (if multiple numeric cols)
    if len(numeric_cols) >= 3:
        # Select top 6 numeric columns
        cols_to_use = numeric_cols[:6]
        corr = df[cols_to_use].corr()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlBu_r',
                   center=0, square=True, linewidths=0.5,
                   cbar_kws={"shrink": 0.8}, ax=ax,
                   annot_kws={"size": 9, "color": "white"})
        ax.set_title('Correlation Matrix', fontsize=14, fontweight='bold', color='white', pad=20)
        ax.tick_params(colors='white')
        
        fig.patch.set_facecolor('#0a0a0a')
        ax.set_facecolor('#0a0a0a')
        
        path = save_chart(fig, "correlation")
        chart_paths.append(path)
        plt.close(fig)
    
    # Chart 4: Missing values (if any)
    missing = df.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False).head(10)
    if len(missing) > 0:
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(missing)))
        bars = ax.barh(missing.index.astype(str), missing.values, color=colors, edgecolor='white', linewidth=0.5)
        ax.set_xlabel('Missing Count', fontsize=12, color='white')
        ax.set_title('Missing Values by Column', fontsize=14, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        ax.invert_yaxis()
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#444')
        ax.spines['bottom'].set_color('#444')
        fig.patch.set_facecolor('#0a0a0a')
        ax.set_facecolor('#0a0a0a')
        
        path = save_chart(fig, "missing")
        chart_paths.append(path)
        plt.close(fig)
    
    return chart_paths[:max_charts]


def save_chart(fig: plt.Figure, prefix: str) -> str:
    """Save chart to file and return the relative path."""
    filename = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
    filepath = CHARTS_DIR / filename
    fig.savefig(filepath, dpi=120, bbox_inches='tight', facecolor='#0a0a0a', edgecolor='none')
    return f"/charts/{filename}"
