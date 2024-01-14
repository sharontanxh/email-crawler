from flask import Flask, jsonify, render_template, request, redirect
from .modules import todos as todos
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


@app.route('/todos', methods=['GET'])
def get_todos():
    """
    Initiate processing of emails and todos
    """
    processed_threads = todos.get_to_do_list()
    todos_list = [todos.thread_to_dict(thread) for thread in processed_threads]
    return jsonify(todos_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=CONFIG.flask_app_port)
