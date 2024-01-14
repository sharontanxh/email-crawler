from .utils import openai_functions
from .models import ToDoResponse
from pydantic import parse_obj_as
from src.helpers.postgres_client import SwiftlyDB
from dateutil import parser

"""
This module contains functions for processing emails and writing them to DB.
"""

def get_to_do_list():
    swiftly_db = SwiftlyDB()
    threads = swiftly_db.get_unprocessed_threads()
    for thread in threads:
        if thread.message_body:
            gpt_output = _get_gpt_response(thread.message_body)
            processed_output = _process_gpt_output(gpt_output)
            if 'next_step' in gpt_output:
                swiftly_db.update_thread(thread.row_id, processed_output)
    processed_threads = swiftly_db.get_processed_threads()
    return processed_threads

def thread_to_dict(thread):
    return {
        'row_id': thread.row_id,
        'thread_id': thread.thread_id,
        'message_body': thread.message_body,
        'subject': thread.subject,
        'from_email': thread.from_email,
        'user_email': thread.user_email,
        'timestamp_of_last_message': thread.timestamp_of_last_message,
        'email_link': thread.email_link,
        'last_updated': thread.last_updated,
        'processed_status': thread.processed_status,
        'user_status': thread.user_status,
        'next_step': thread.next_step,
        'action': thread.action,
        'deadline': thread.deadline,
        'summary': thread.summary,
        'effort': thread.effort,
        'todo_constraint': thread.todo_constraint
    }

def _process_gpt_output(gpt_output: dict) -> dict:
    valid_next_steps = ['todo', 'review', 'digest']
    if gpt_output.get('next_step') not in valid_next_steps:
        gpt_output['next_step'] = 'review'

    valid_efforts = ['low', 'medium', 'high']
    if gpt_output.get('effort') not in valid_efforts:
        gpt_output['effort'] = 'medium'

    if not gpt_output.get('action') or gpt_output.get('action') == 'None':
        gpt_output['action'] = None
    
    if not gpt_output.get('constraint') or gpt_output.get('constraint') == 'None':
        gpt_output['constraint'] = None

    if gpt_output.get('next_step') in ['todo', 'review'] and gpt_output.get('deadline'):
        try:
            gpt_output['deadline'] = parser.parse(gpt_output['deadline'])
        except:
            gpt_output['deadline'] = None
    else:
        gpt_output['deadline'] = None

    if not gpt_output.get('summary'):
        gpt_output['summary'] = None

    return gpt_output

def _get_gpt_response(email_string) -> dict:
    """
    Gets GPT response for a given email string, with a conservative string length
    """
    system_prompt = _create_system_prompt()
    user_prompt = "Email:\n" + email_string
    if len(user_prompt) > 20000:
        user_prompt = user_prompt[:20000]
    response = openai_functions.call_gpt(system_prompt, user_prompt)
    return _check_response(response)

def _create_system_prompt() -> str:
    """
    Returns a prompt asking GPT to parse the email and assess follow-up items
    """
    prompt = f'''You are a helpful personal assistant. Process the email given and return the output in strict JSON with the following fields:
   
    {{
    "next_step": "if a follow-up is absolutely required, return 'todo';
                  if a follow-up is suggested but not absolutely required, return 'review';
                  if no follow-ups are needed, return 'digest'",
    "action": "if next_step is 'todo' or 'review', return the suggested action. Otherwise, return 'None'",
    "deadline": "if next_step is 'todo' or 'review', return the suggested deadline for the action. Otherwise, return 'None'",
    "summary": "summarize the email in two sentences",
    "effort": "estimate the effort level for the action - 'low', 'medium', or 'high'",
    "constraint: "if next_step is 'todo' or 'review', extract any other information that can inform the suggested action, such as office hours, phone number, etc. Return a dictionary wiht the relevant keys, or 'None'" 
    }}
    ''' 
    return prompt

def _check_response(response) -> str:
    """
    Check the GPT response, parse it if necessary
    """
    try:
        response = parse_obj_as(ToDoResponse, response)
        return response.dict()
    except Exception as e:
        return {"Error": f"{str(e)} from {response}"}