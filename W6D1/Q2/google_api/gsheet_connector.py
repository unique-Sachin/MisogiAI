import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

def get_gsheet_client():
    creds = Credentials.from_service_account_file(
        'credentials/service_account.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    return gspread.authorize(creds)

def read_sheet(spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
    print(f"Reading sheet: {sheet_name} from spreadsheet ID: {spreadsheet_id}")
    client = get_gsheet_client()
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    records = sheet.get_all_records()
    return pd.DataFrame(records)

def write_sheet(spreadsheet_id: str, sheet_name: str, df: pd.DataFrame):
    client = get_gsheet_client()
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    sheet.clear()
    data = [df.columns.tolist()] + df.values.tolist()
    sheet.insert_rows(data)

def get_worksheet_names(spreadsheet_id: str) -> list:
    """
    Returns a list of worksheet names for the given spreadsheet ID.
    """
    client = get_gsheet_client()
    sheet = client.open_by_key(spreadsheet_id)
    return [ws.title for ws in sheet.worksheets()]
