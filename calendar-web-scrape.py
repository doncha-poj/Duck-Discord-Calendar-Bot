import os.path
import base64
from bs4 import BeautifulSoup
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_credentials():
    """Shows basic usage of the Gmail API.
    Handles authentication and returns creds
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
              "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
          token.write(creds.to_json())
    return creds

def html_scrape(html_file):
    """Grabs the national days from html"""
    

def calendar_scrape():
    """Scrapes the national days from email
    """
    try:
        creds = get_credentials()
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        print("Successfully connected to Gmail API.")

        # Search for latest email from newsletter
        sender = "newsletter@mail.nationaldaycalendar.com"
        query = f"from:{sender}"
        results = service.users().messages().list(userId="me", q=query, maxResults=1).execute()

        messages = results.get("messages", [])

        if not messages:
            print(f"No emails found from {sender}")
            return

        # Get the most recent message
        msg_id = messages[0]["id"]
        message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        print(message)

        # The email body is in the 'parts' or 'payload' section
        payload = message.get("payload", {})
        parts = payload.get("parts", [])

        html_payload = ""
        for part in parts:
            if part["mimeType"] == "text/html":
                data = part["body"]["data"]
                # The data is base64url encoded, so we need to decode it
                html_payload = base64.urlsafe_b64decode(data).decode("utf-8")
                break
        # print(html_payload)
        if not html_payload:
            print("Could not find HTML content in the email.")
            return

        # Save the HTML to a file so you can inspect it.
        with open("email_content.html", "w", encoding="utf-8") as f:
            f.write(html_payload)
        print("Saved email content to email_content.html for inspection.")

        holidays = html_scrape(html_file=html_payload)

    # Error handling
    except HttpError as error:
        print(f"An error occurred: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e} ")




if __name__ == "__main__":
    if os.path.exists("email_content.html"):
        print("performing scrape")
        html_scrape("email_content.html")
    else:
        print("nope")
