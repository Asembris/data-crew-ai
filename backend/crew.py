"""
CrewAI Agent Definitions
Specialized agents for data analysis, statistics, and Plotly visualizations.
"""
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tools import CSVSearchTool

PLOTLY_INSTRUCTIONS = """
Create Plotly charts. Return ONLY valid JSON.

SIMPLE BAR:
{"data": [{"x": ["A", "B"], "y": [10, 20], "type": "bar", "marker": {"color": "#8b5cf6"}}], "layout": {"title": "Title"}}

PIE:
{"data": [{"labels": ["A", "B"], "values": [10, 20], "type": "pie"}], "layout": {"title": "Title"}}

GROUPED BAR (for comparing categories):
{"data": [
  {"x": ["Group1", "Group2"], "y": [10, 15], "type": "bar", "name": "Male", "marker": {"color": "#1f77b4"}},
  {"x": ["Group1", "Group2"], "y": [20, 25], "type": "bar", "name": "Female", "marker": {"color": "#ff7f0e"}}
], "layout": {"title": "Title", "barmode": "group"}}

STACKED BAR:
{"data": [
  {"x": ["A", "B"], "y": [10, 15], "type": "bar", "name": "Cat1"},
  {"x": ["A", "B"], "y": [20, 25], "type": "bar", "name": "Cat2"}
], "layout": {"title": "Title", "barmode": "stack"}}

HISTOGRAM:
{"data": [{"x": [1,2,3,4,5], "type": "histogram", "marker": {"color": "#8b5cf6"}}], "layout": {"title": "Title"}}

RULES:
1. "data" must be an ARRAY
2. For grouped charts, create SEPARATE trace objects for each category
3. Return ONLY JSON, no markdown, no explanation
4. First use the tool to get the exact data values, then build the JSON
"""


def create_crew(csv_path: str):
    csv_tool = CSVSearchTool(csv_path=csv_path)
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    analyst = Agent(
        role='Data Analyst',
        goal='Answer data questions concisely.',
        backstory="Give SHORT, DIRECT answers in 1-2 sentences. No recommendations.",
        tools=[csv_tool],
        verbose=True,
        memory=True,
        allow_delegation=False,
        max_iter=5,
        llm=llm
    )

    statistician = Agent(
        role='Statistician',
        goal='Calculate and return statistics.',
        backstory="Return just the numbers. Example: 'Mean: 29.7, Median: 28.0'",
        tools=[csv_tool],
        verbose=True,
        memory=True,
        allow_delegation=False,
        max_iter=5,
        llm=llm
    )

    visualizer = Agent(
        role='Visualizer',
        goal='Create Plotly chart JSON.',
        backstory=f"You create Plotly charts.\n\n{PLOTLY_INSTRUCTIONS}",
        tools=[csv_tool],
        verbose=True,
        memory=True,
        allow_delegation=False,
        max_iter=8,  # More iterations for complex charts
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    )

    return analyst, statistician, visualizer


def run_analysis(csv_path: str, query: str, agent_type: str = "analyst"):
    """Execute a query with the specified agent."""
    analyst, statistician, visualizer = create_crew(csv_path)
    
    if agent_type == "statistician":
        task = Task(
            description=f"Calculate: {query}. Return ONLY the numbers.",
            expected_output="Numbers only.",
            agent=statistician
        )
    elif agent_type == "visualizer":
        task = Task(
            description=(
                f"Create a Plotly chart for: {query}\n\n"
                "Steps:\n"
                "1. Use the tool to query the data: df.groupby(...).size() or value_counts()\n"
                "2. Build the Plotly JSON with the exact values\n"
                "3. Return ONLY the JSON\n\n"
                "For multi-category comparisons, use barmode: 'group'"
            ),
            expected_output="Valid Plotly JSON only.",
            agent=visualizer
        )
    else:
        task = Task(
            description=f"Answer briefly: {query}",
            expected_output="1-2 sentence answer.",
            agent=analyst
        )

    crew = Crew(agents=[analyst, statistician, visualizer], tasks=[task], process=Process.sequential)
    
    try:
        result = crew.kickoff()
        return result.raw if hasattr(result, 'raw') else str(result)
    except Exception as e:
        return f"Error: {str(e)}"
