import os.path
import base64
import re

from bs4 import BeautifulSoup
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _get_credentials():
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

def _html_scrape(html_file: str) -> list[str]:
    """Grabs the national days from html"""

    def clean_text(text: str) -> str:
        """Replaces common Unicode symbols with their ASCII equivalents."""
        replacements = {
            '\u2122': '(TM)',  # Trademark
            '\u00ae': '(R)',  # Registered
            '\u00a9': '(C)',  # Copyright
            '\u2013': '-',  # En Dash
            '\u2014': '-',  # Em Dash
            '\u2026': '...',  # Ellipsis
            '\u2019': "'",  # Smart Apostrophe
            '\u201c': '"',  # Smart Quote
            '\u201d': '"',  # Smart Quote
        }
        for unicode_char, ascii_char in replacements.items():
            text = text.replace(unicode_char, ascii_char)
        return text

    soup = BeautifulSoup(html_file, 'html.parser')
    holiday_list = []

    # Get today's date
    today_str_format = datetime.date.today()
    date_string = today_str_format.strftime("%B %d, %Y").upper()
    # print(date_string)

    date_tag = soup.find(string=re.compile(date_string, re.IGNORECASE))

    if date_tag:
        # The pipe-separated list is in the parent <span> of the date tag.
        parent_span = date_tag.find_parent('span')
        if parent_span:
            # Get the raw text, which includes the date and all holidays.
            full_text = parent_span.get_text(separator=' ', strip=True)

            # Split the string by the pipe character.
            parts = full_text.split('|')

            # The first part is the date, so we take everything after it.
            # We also strip extra whitespace from each holiday name.
            holiday_list = [clean_text(part.strip()) for part in parts[1:]]

    return holiday_list

def get_todays_holidays():
    """Scrapes the national days from email
    """
    try:
        creds = _get_credentials()
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
            return []

        # Get the most recent message
        msg_id = messages[0]["id"]
        message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        # print(message)

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
            return []

        if html_payload:
            # Save the fresh HTML to a file for future local testing
            with open("email_content.html", "w", encoding="utf-8") as f:
                f.write(html_payload)
            print("Saved fresh email content to email_content.html.")
            return _html_scrape(html_payload)
        else:
            print("Could not find HTML content in the email.")
            return []

    # Error handling
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e} ")
        return []


# Only runs if this file is executed directly
if __name__ == "__main__":
    holidays = []

    # Check if a local HTML file exists for testing
    if os.path.exists("email_content.html"):
        print("Found local 'email_content.html'. Parsing from file to avoid API call...")
        with open("email_content.html", 'r', encoding='utf-8') as f:
            local_html_content = f.read()
        holidays = _html_scrape(local_html_content)
    else:
        # If no local file, call the main function to fetch from the API
        print("No local 'email_content.html' found. Fetching from Gmail API...")
        holidays = get_todays_holidays()

    # Print the results, regardless of where they came from
    if holidays:
        today_str = datetime.date.today().strftime("%B %d, %Y")
        print("\n" + "=" * 40)
        print(f"    National Days for {today_str}")
        print("=" * 40)
        for day in holidays:
            print(f"- {day}")
        print("=" * 40)
    else:
        today = datetime.date.today().strftime("%B %d, %Y").upper()
        print(f"Could not find the date '{today}' or parse holidays from the email.")