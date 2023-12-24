from flask import Flask, render_template, request, redirect
import modules.models as models
import modules.todos as todos
import os

from src.config import CONFIG
from src.helpers.gmail_client import GmailScraper


from src.config import CONFIG
from src.helpers.gmail_client import GmailScraper


app = Flask(__name__)


@app.route('/healthcheck')
def healthcheck():
    print('')
    return "Alive", 200


@app.route('/login')
def login():
    return "Alive", 200


@app.route('/fetch_emails_db')
def fetch_emails_db():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        credentials_file = os.path.join(parent_dir, 'credentials.json')

        gmail_scraper = GmailScraper(credentials_file)
        gmail_scraper.write_to_db()
    except Exception:
        return "Error Fetching Emails", 500
    return "Fetched", 200


@app.route('/fetch_emails_csv')
def fetch_emails_csv():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)

        credentials_file = os.path.join(parent_dir, 'credentials.json')
        csv_file_name = os.path.join(parent_dir, 'emails.csv')

        gmail_scraper = GmailScraper(credentials_file)
        gmail_scraper.write_csv_file(csv_file_name)
    except Exception:
        return "Error Fetching Emails", 500
    return "Fetched", 200


@app.route('/init')
def initialize():
    print('Initializing...')
    return render_template('index.html')


@app.route('/form')
def test_form():
    return render_template('test-form.html')


@app.route('/form', methods=['POST'])
def test_form_post():
    text = request.form['text']
    processed_text = text.upper()
    msg = "{}".format(processed_text)
    return msg


# We may not need this - can just use the streamlit app to make requests to our Flask API
@app.route('/home')
def home():
    redirect("http://localhost:8501")


@app.route('/todos', methods=['GET'])
def get_todos():
    """
    Return json object which will be read by streamlit frontend as a pandas dataframe and displayed
    """
    todos.get_to_do_list()
    return "Success", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=CONFIG.flask_app_port)
