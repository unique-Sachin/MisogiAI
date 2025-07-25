from langchain.agents import Tool
from google_api.gsheet_connector import read_sheet, write_sheet
import pandas as pd

def filter_data(df: pd.DataFrame, column: str, condition: str) -> pd.DataFrame:
    try:
        return df.query(f"{column} {condition}")
    except Exception:
        return df[df[column] == condition]  # fallback to exact match

def pivot_table(df: pd.DataFrame, index: str, columns: str, values: str, aggfunc='sum') -> pd.DataFrame:
    return pd.pivot_table(df, index=index, columns=columns, values=values, aggfunc=aggfunc).reset_index()


from pydantic import BaseModel, Field
from langchain_core.tools import tool

class ReadSheetArgs(BaseModel):
    spreadsheet_id: str = Field(..., description="Google Sheets spreadsheet ID")
    sheet_name: str = Field(..., description="Name of the worksheet")

@tool(args_schema=ReadSheetArgs)
def read_worksheet(spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
    """Load a worksheet from Google Sheets."""
    print(f"Loading worksheet: {sheet_name} from spreadsheet ID: {spreadsheet_id}")
    return read_sheet(spreadsheet_id, sheet_name)

def get_tools():
    return [
        # Tool(name="read_worksheet", func=read_worksheet_tool, description="Load worksheet from Google Sheets"),
        # Tool(name="filter_data", func=filter_data, description="Filter a DataFrame with a condition"),
        # Tool(name="pivot_table", func=pivot_table, description="Create a pivot table from the data"),
        # Tool(name="write_results", func=write_sheet, description="Write results back to Google Sheet")
        read_worksheet,
    ]

