# Swiftly: The next-generation email crawler 
<img src="https://github.com/sharontanxh/email-crawler/assets/81359638/6df730c4-a9e7-4c3c-8bb5-86596099897c" width="60" height="60">

### Introduction

Work-in-progress hackathon project from HACKHERS 2023.

Have you ever struggled to get a handle on your email? Wouldn't it be great if your email client could intelligently figure out which emails needed follow-up actions and create your to-do list automatically?

### Project Structure

- gpt_client.py: Authenticate and pull emails
- streamlit_main.py: Main streamlit page for prototype UI
- email_classification.ipynb: Generate LLM output from emails


# email-crawler

To run app locally
`pip install -r requirements.txt`
`cd src`
`flask run`

The app runs on port 5000, you can check 
`http://127.0.0.1:5000/init`

quick command to kill any process running on port 5000
`kill -9 $(lsof -i:8080 -t) 2> /dev/null`
