import os
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dateutil import parser
import base64
import csv


class GmailScraper:
    def __init__(self, credentials_file, token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self.build_service()

    def build_service(self):
        try:
            creds = None
            # The file token.json stores the user's access and refresh tokens.

            flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, ['https://www.googleapis.com/auth/gmail.readonly']
                    )
            creds = flow.run_local_server(port=0)
            service = build('gmail', 'v1', credentials=creds)
            return service
        except Exception as e:
            print(f"Error building Gmail service: {str(e)}")
            return None


    def scrape_recent_threads(self):
        try:
            threads = self.service.users().threads().list(userId='me', maxResults=50, q="-category:promotions").execute().get('threads', [])
            results = []
            for thread in threads:

                thread_id = thread['id']
                thread_data = self.service.users().threads().get(userId='me', id=thread_id).execute()

                message = thread_data['messages'][0]  # Get the first message in the thread

                for header in message['payload']['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']

                    if header['name'] == 'From':
                        from_split = header['value'].split("<")[1]
                        from_email = from_split[0:-1]

                    if header['name'] == 'Date':
                        timestamp = parser.parse(header['value']) if header['value'] is not None else None

                email_link = f"https://mail.google.com/mail/u/0/#inbox/{thread_id}"

                encoded_message_body = ""

                if hasattr(message['payload']['body'], 'data'):
                    print("the payload body had a data")
                    try:
                        encoded_message_body = message['payload']['body']['data']
                    except AttributeError:
                        print("there was no data in payload body")
                else:
                    print("the payload body didn't have a data")
                    print(message[])
                    if hasattr(message['payload'], 'parts'):
                        print("the payload had parts")
                        first_part = message['payload']['parts'][0]
                        encoded_message_body = first_part['body']['data']
                    else:
                        print("the payload didn't have parts")

                # Decode the base64-encoded string
                decoded_bytes = base64.b64decode(encoded_message_body)
                # Convert the bytes to a string
                decoded_string = decoded_bytes.decode('utf-8')

                thread_info = {
                    'thread_id': thread_id,
                    'message_body': decoded_string,
                    'subject': subject,
                    'from': from_email,
                    'timestamp_of_last_message': timestamp,
                    'email_link': email_link
                }
                results.append(thread_info)
            return results
        except Exception as e:
            print(f"Error scraping recent threads: {str(e)}")
            return []



credentials_file = 'credentials.json'
gmail_scraper = GmailScraper(credentials_file)
recent_threads = gmail_scraper.scrape_recent_threads()

# Specify the CSV file name
csv_file_name = 'emails.csv'

# Define the CSV column headers
fieldnames = ['thread_id', 'message_body', 'subject', 'from', 'timestamp_of_last_message', 'email_link']

# Open the CSV file for writing
with open(csv_file_name, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write the header row
    writer.writeheader()

    # Write the data rows
    for item in recent_threads:
        writer.writerow(item)

print(recent_threads)
