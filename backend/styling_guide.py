"""
Plotly Styling Guide
Provides styling instructions for different chart types.
Based on the blog post approach of storing styling preferences.
"""

PLOTLY_STYLING = {
    "general": """
    GENERAL STYLING RULES:
    - Always use dark background colors (#0a0a0a for background)
    - Use white/light gray text for labels
    - Primary color: #8b5cf6 (purple)
    - Secondary colors: #3b82f6 (blue), #10b981 (green), #f59e0b (amber)
    - Always include a descriptive title
    - Format large numbers as K (thousands) or M (millions)
    - Show percentages with 2 decimal places and '%' sign
    """,
    
    "bar": """
    BAR CHART STYLING:
    - Use colorful bars with the primary color palette
    - Add value annotations on top of bars
    - Keep x-axis labels readable (rotate if needed)
    - For grouped bars, use barmode='group' and legend
    """,
    
    "horizontal_bar": """
    HORIZONTAL BAR CHART STYLING:
    - Use orientation='h' for all traces
    - Add value annotations at end of bars
    - Order bars by value if possible
    - Good for comparing categories with long names
    """,
    
    "scatter": """
    SCATTER PLOT STYLING:
    - Use mode='markers' for scatter points
    - Add a trendline in a contrasting color (#ef4444 red, dashed)
    - Include axis labels for both x and y
    - Use opacity=0.6-0.8 for overlapping points
    - Add correlation coefficient in annotation if relevant
    """,
    
    "histogram": """
    HISTOGRAM STYLING:
    - Use 20-30 bins for smooth distribution
    - Add mean line as vertical annotation
    - Include count on y-axis
    - Use single color with slight transparency
    """,
    
    "pie": """
    PIE CHART STYLING:
    - Limit to 6-8 slices, combine small values as 'Other'
    - Use hole=0.4 for donut style
    - Add percentage labels on slices
    - Use contrasting colors for adjacent slices
    """,
    
    "line": """
    LINE CHART STYLING:
    - Use mode='lines+markers' for visibility
    - Add markers at data points
    - Annotate min and max values
    - Use different colors for multiple lines
    """,
    
    "heatmap": """
    HEATMAP STYLING:
    - Use 'RdBu' colorscale for correlation matrices
    - Set zmid=0 for diverging colors
    - Add text annotations for values
    - Include colorbar
    """,
    
    "grouped_bar": """
    GROUPED BAR CHART STYLING:
    - Use barmode='group'
    - Each group should have distinct colors
    - Include legend for group labels
    - Keep bar width consistent
    """,
    
    "box": """
    BOX PLOT STYLING:
    - Show individual points if data is small
    - Use different colors for each box
    - Include outliers
    - Add mean marker
    """
}


def get_styling_instructions(chart_type: str) -> str:
    """Get styling instructions for a specific chart type."""
    general = PLOTLY_STYLING["general"]
    specific = PLOTLY_STYLING.get(chart_type, "")
    return f"{general}\n\n{specific}"


def get_chart_template(chart_type: str) -> str:
    """Get a code template for a specific chart type."""
    
    templates = {
        "bar": '''
{
    "data": [{
        "x": ["Category1", "Category2", "Category3"],
        "y": [value1, value2, value3],
        "type": "bar",
        "marker": {"color": ["#8b5cf6", "#3b82f6", "#10b981"]},
        "text": [value1, value2, value3],
        "textposition": "outside"
    }],
    "layout": {
        "title": "Chart Title",
        "xaxis": {"title": "X Label"},
        "yaxis": {"title": "Y Label"}
    }
}''',
        
        "horizontal_bar": '''
{
    "data": [{
        "x": [value1, value2, value3],
        "y": ["Category1", "Category2", "Category3"],
        "type": "bar",
        "orientation": "h",
        "marker": {"color": "#8b5cf6"}
    }],
    "layout": {
        "title": "Chart Title",
        "xaxis": {"title": "Count"},
        "yaxis": {"title": "Category"}
    }
}''',

        "grouped_bar": '''
{
    "data": [
        {"x": ["Group1", "Group2"], "y": [v1, v2], "type": "bar", "name": "Series1", "marker": {"color": "#8b5cf6"}},
        {"x": ["Group1", "Group2"], "y": [v3, v4], "type": "bar", "name": "Series2", "marker": {"color": "#3b82f6"}}
    ],
    "layout": {
        "title": "Grouped Chart Title",
        "barmode": "group",
        "showlegend": true
    }
}''',
        
        "scatter": '''
{
    "data": [
        {"x": [x_values], "y": [y_values], "type": "scatter", "mode": "markers", "name": "Data", "marker": {"color": "#8b5cf6", "opacity": 0.7}},
        {"x": [x_trend], "y": [y_trend], "type": "scatter", "mode": "lines", "name": "Trend", "line": {"color": "#ef4444", "dash": "dash"}}
    ],
    "layout": {
        "title": "Scatter Plot Title",
        "xaxis": {"title": "X Variable"},
        "yaxis": {"title": "Y Variable"}
    }
}''',
        
        "histogram": '''
{
    "data": [{
        "x": [numeric_values],
        "type": "histogram",
        "marker": {"color": "#8b5cf6"},
        "nbinsx": 25
    }],
    "layout": {
        "title": "Distribution of Variable",
        "xaxis": {"title": "Value"},
        "yaxis": {"title": "Frequency"}
    }
}''',
        
        "pie": '''
{
    "data": [{
        "labels": ["Label1", "Label2", "Label3"],
        "values": [value1, value2, value3],
        "type": "pie",
        "hole": 0.4,
        "marker": {"colors": ["#8b5cf6", "#3b82f6", "#10b981"]}
    }],
    "layout": {"title": "Pie Chart Title"}
}'''
    }
    
    return templates.get(chart_type, templates["bar"])
