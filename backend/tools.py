import pandas as pd
from crewai.tools import BaseTool

class CSVSearchTool(BaseTool):
    name: str = "CSV Search and Analysis Tool"
    description: str = (
        "Useful to search and analyze data within a CSV file. "
        "The file is loaded into a pandas DataFrame called `df`. "
        "Input should be a python expression that operates on `df` and returns a result. "
        "Examples: `df.head()`, `df.describe()`, `df['column'].mean()`, `df.corr()`. "
        "IMPORTANT: Do NOT use `self.df`, just use `df` directly."
    )
    df: pd.DataFrame = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, csv_path: str):
        super().__init__()
        try:
            self.df = pd.read_csv(csv_path)
        except Exception as e:
            raise ValueError(f"Failed to load CSV from {csv_path}: {e}")

    def _run(self, query: str) -> str:
        """
        Executes python code on the dataframe.
        SAFEGUARD: This is a demo. In prod, use safer sandboxing (e.g. E2B).
        """
        # Creating a local scope with the dataframe
        local_scope = {'df': self.df, 'pd': pd}
        try:
            # We wrap the query in a way that captures the last expression or print output
            # A simple way for agents: they usually write: "df.head()" or "df['col'].mean()"
            # We can try to eval, if fails, exec.
            
            # Simple restricted eval/exec
            exec(f"result = {query}", {}, local_scope)
            return str(local_scope.get('result', 'No result returned'))
        except SyntaxError:
            try:
                # If it's a statement (like print), exec it
                # We divert stdout to capture print statements
                import io
                import sys
                captured_output = io.StringIO()
                sys.stdout = captured_output
                exec(query, {}, local_scope)
                sys.stdout = sys.__stdout__
                return captured_output.getvalue().strip() or "Code executed successfully."
            except Exception as e:
                return f"Error executing code: {e}"
        except Exception as e:
            return f"Error executing code: {e}"
