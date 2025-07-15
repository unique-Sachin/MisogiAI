import os
import base64
from typing import List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def _get_service(credentials_file: str):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

class GmailClient:
    def __init__(self, credentials_file: str):
        self.service = _get_service(credentials_file)

    def fetch_unread(self, max_results: int = 10):
        results = self.service.users().messages().list(userId="me", labelIds=["UNREAD"], maxResults=max_results).execute()
        messages = results.get("messages", [])
        full = []
        for m in messages:
            msg = self.service.users().messages().get(userId="me", id=m["id"], format="full").execute()
            full.append(msg)

        # Sort by internalDate (milliseconds since epoch) descending so newest first
        full.sort(key=lambda m: int(m.get("internalDate", 0)), reverse=True)
        return full

    def send_message(self, to: str, subject: str, body: str):
        message = f"Subject: {subject}\nTo: {to}\nContent-Type: text/plain; charset=utf-8\n\n{body}"
        encoded = base64.urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")
        self.service.users().messages().send(userId="me", body={"raw": encoded}).execute()

    def mark_as_read(self, msg_id: str):
        self.service.users().messages().modify(userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}).execute() 