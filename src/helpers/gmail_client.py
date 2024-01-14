import os
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime
from dateutil import parser
import base64
import quopri
import csv
import email

from src.helpers.postgres_client import SwiftlyDB


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

    def decode_mime_content(self, message_body, content_transfer_encoding):
        """
        Decodes a MIME message body based on its Content-Transfer-Encoding.

        :param message_body: The raw body of the MIME message (a string).
        :param content_transfer_encoding: The encoding type (from the message headers).
        :return: The decoded message body.
        """

        if not content_transfer_encoding:
            raise ValueError("No Content Transfer Encoding Found")

        # Normalize the encoding string
        encoding = content_transfer_encoding.lower().strip()

        # Decode based on the specified content transfer encoding
        if encoding == '7bit' or encoding == '8bit' or encoding == 'binary':
            # These encodings are essentially plaintext. 'binary' might need further processing depending on the context.
            return message_body
        elif encoding == 'base64':
            # Decode the base64 encoded message
            message_body = self.ensure_base64_padding(message_body)
            return base64.b64decode(message_body).decode('utf-8')
        elif encoding == 'quoted-printable':
            # Decode the quoted-printable encoded message
            return quopri.decodestring(message_body).decode('utf-8')
        else:
            # Unknown encoding
            raise ValueError(f"Unsupported encoding: {content_transfer_encoding}")

    def ensure_base64_padding(self, data):
        '''Base64-encoded data should have a length that is a multiple of 4.
        If the data is not a multiple of 4 characters long, it's typically
        padded with '=' characters to make up the length.'''

        # Check the length of the data
        missing_padding = len(data) % 4

        # If there is missing padding, add the necessary '=' characters
        if missing_padding:
            data += '=' * (4 - missing_padding)

        return data

    def scrape_recent_threads(self):
        results = []
        timestamp_processed = datetime.utcnow()
        
        try:
            threads = self.service.users().threads().list(userId='me', maxResults=2, q="-category:promotions").execute().get('threads', [])

            for thread in threads:
                thread_id = thread['id']
                email_link = f"https://mail.google.com/mail/u/0/#inbox/{thread_id}"
                thread_data = self.service.users().threads().get(userId='me', id=thread_id).execute()
                
                if not thread_data.get('messages'):
                    continue

                message = thread_data['messages'][0]  # Get the first message in the thread
                encoding_type = None

                for header in message['payload']['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']

                    if header['name'] == 'To':
                        to_email = header['value']

                    if header['name'] == 'From' and '<' in header['value']:
                        from_split = header['value'].split("<")[1]
                        from_email = from_split[0:-1]

                    if header['name'] == 'Date':
                        timestamp = parser.parse(header['value']) if header['value'] is not None else None

                    if header['name'] == 'Content-Transfer-Encoding':
                        encoding_type = header['value']

                # Extract the message body
                encoded_message_body = ""
                if 'data' in message['payload']['body']:
                    print("the payload had a body")
                    encoded_message_body = message['payload']['body']['data']
                elif 'parts' in message['payload']:
                    print("the payload had parts")
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            headers = part['headers']
                            encoding_type_headers = [header['value'] for header in headers if header['name'] == 'Content-Transfer-Encoding']
                            encoding_type = encoding_type_headers[0] if len(encoding_type_headers) > 0 else ""
                            encoded_message_body = part['body']['data']

                # Decode MIME content based on Content-Transfer-Encoding header value
                decoded_message = ""
                try:
                    decoded_bytes = base64.urlsafe_b64decode(encoded_message_body)
                    message = email.message_from_bytes(decoded_bytes)
                    decoded_message = message.as_string().strip()
                except Exception as e:
                    print(f"Could not decode: {str(e)} with encoding type {encoding_type}")

                thread_info = {
                    'thread_id': thread_id,
                    'message_body': decoded_message,
                    'subject': subject,
                    'from': from_email,
                    'user': to_email,
                    'timestamp_of_last_message': timestamp,
                    'email_link': email_link,
                    'updated_utc': timestamp_processed
                }
                results.append(thread_info)
        except Exception as e:
            print(f"Error scraping recent threads: {str(e)}")
            print(f"Returning results scraped so far: {len(results)}")
            return results
        return results

    def write_csv_file(self, file_name):
        '''
        This scrapes recent threads and writes them to a CSV file
        '''
        recent_threads = self.scrape_recent_threads()

        # Define the CSV column headers
        fieldnames = ['thread_id', 'message_body', 'subject', 'from', 'user', 'timestamp_of_last_message', 'email_link', 'updated_utc']

        # Open the CSV file for writing
        with open(file_name, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Write the header row
            writer.writeheader()

            # Write the data rows
            for item in recent_threads:
                writer.writerow(item)
        print(f"{file_name} has been written to disk")

    def write_to_db(self):
        '''
        This scrapes recent threads and writes them to Postgres Db
        '''
        recent_threads = self.scrape_recent_threads()
        print(f"Scraped {len(recent_threads)} threads from Gmail")
        
        db = SwiftlyDB()

        threads_data = []
        for item in recent_threads:
            thread_data = {
                'thread_id': item['thread_id'],
                'message_body': item['message_body'],
                'subject': item['subject'],
                'from_email': item['from'],
                'user_email': item['user'],
                'timestamp_of_last_message': item['timestamp_of_last_message'],
                'email_link': item['email_link'],
                'processed_status': False,
                'last_updated': item['updated_utc'],
                'user_status': None
            }
            threads_data.append(thread_data)

        try:
            db.add_threads(threads_data)
            print(f"Added {len(recent_threads)} threads to DB")
        except Exception as e:
            print(f"An error occurred while writing to the database: {e}")
