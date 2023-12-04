import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
import pandas as pd
import gpt_calls
import asyncio

# Globals

def main():
    st.set_page_config(page_title="Email Crawler Demo", page_icon=":envelope:", layout="wide")
    col_a, col_b = st.columns([1, 13])
    with col_a:
        st.image('./Assets/logo-no-bg.png', width=75)
    with col_b:
        st.header("Swiftly: Spend time on people and passions - not email")

    col1, col2 = st.columns([3.5, 1.5], gap="large")
    
    st.session_state.authenticated = True # TODO: Modify to track authentication status
    
    with col1: 
        st.subheader("To Do")
        st.write("There are messages that require an action from you soon.")
        # if st.button("Call GPT-4"):
        #     asyncio.run(call_gpt_with_query(table))

        if not st.session_state.authenticated:
            st.error("Please log-in to Google first.")

        df = get_digest_list()
        df_for_display = df[['summary', 'effort', 'See more']]
        table = st.data_editor(df_for_display)
        selected_indices = table[table['See more'] == True].index.tolist()
        if selected_indices:
            st.session_state.selected_row = df.iloc[selected_indices[0]]  # Always take the first selected row
            st.session_state.show_more = True
        else:
            st.session_state.show_more = False

        st.subheader("To Review")
        st.write("Organize, delete, or unsubscribe from messages to reduce noise in your inbox.")
        
        # df1 = get_review_list()
        # table1 = st.data_editor(df1)
        # selected_indices = table1[table1['See more'] == True].index.tolist()
        # if selected_indices:
        #     st.session_state.selected_row1 = df1.iloc[selected_indices[0]]
        #     st.session_state.show_more1 = True
        # else:
        #     st.session_state.show_more1 = False

        st.subheader("Digest")
        st.write("Read or create a summary from your favourite newsletters and organizations.")
        
        df2 = get_digest_list()['next_step', '']
        table2 = st.data_editor(df2)
        selected_indices = table2[table2['See more'] == True].index.tolist()
        if selected_indices:
            st.session_state.selected_row2 = df2.iloc[selected_indices[0]]
            st.session_state.show_more2 = True
        else:
            st.session_state.show_more2 = False  
    
    with col2:
        if st.session_state.show_more:
            st.subheader("Take action")
            if st.session_state.selected_row['summary']:
                st.write("**Description**")
                st.write(st.session_state.selected_row['summary'])
            
            if st.session_state.selected_row['action'] and st.session_state.selected_row['action']!="None":
                st.write("**Suggested action**")
                st.write(st.session_state.selected_row['action'])
            
            if st.session_state.selected_row['deadline'] and st.session_state.selected_row['deadline']!="None":
                st.write("**Deadline**")
                st.write(st.session_state.selected_row['deadline'])

            if st.session_state.selected_row['constraint'] and st.session_state.selected_row['constraint']!="None":
                st.write("**Take note**")
                constraint_list = eval(st.session_state.selected_row['constraint'])
                for constraint in constraint_list:
                    st.write(f" - {constraint}")
            
            # if st.session_state.selected_row['email_link']:
            st.button(":arrow_upper_right: View in Gmail")

            if st.session_state.selected_row['action']:
                st.button(":calendar: Add to calendar")
        # if st.session_state.show_more1:
        #     st.write(st.session_state.selected_row1)

        # if st.session_state.show_more2:
        #     st.write(st.session_state.selected_row2)

    # with st.sidebar:
    #     st.subheader("Take action")

def get_to_do_list() -> pd.DataFrame:
    # To be implemented
    # Make a dataframe with columns Done, Task, From, Effort, Urgency, Source
    df = pd.DataFrame({'Summary': ["Payment due for card ending 9999", "Failed delivery attempt"], 'Action': ["Chase Bank", "FedEx"], 'Effort': ["Low", "Medium"], 'Urgency': ["Today", "Tomorrow"], 'Source': ["Email", "Email"], 'See more': [False, False]})
    return df

def get_review_list() -> pd.DataFrame:
    # To be implemented
    # Make a dataframe with columns Done, Task, From, Effort, Urgency, Source
    df = pd.DataFrame({'Task': ["Payment due for card ending 1234", "Failed delivery attempt"], 'From': ["Chase Bank", "FedEx"], 'Effort': ["Low", "Medium"], 'Urgency': ["Today", "Tomorrow"], 'Source': ["Email", "Email"], 'See more': [False, False]})
    return df

def get_digest_list() -> pd.DataFrame:
    # To be implemented
    # Make a dataframe with columns Done, Task, From, Effort, Urgency, Source
    # df = pd.DataFrame({
    # "summary": "The email is a notification about upcoming Generative AI events in San Francisco, with a list of dates and event names. The sender, Sahar, invites the recipient to attend these events and provides a link for more information.",
    # "is_todo": "Y",
    # "action": "Mark the dates of the events of interest and plan to attend them.",
    # "effort": "Medium",
    # "deadline": "The events are scheduled from November 30th to January 18, 2024. The deadline would be the date of each specific event.",
    # "constraint": ["The events are in-person, so physical presence in San Francisco is required.", "Some events may require prior registration or application.", "The exact location and time of each event should be checked on the provided website."],
    # })
    df = get_and_enhance_input()
    df = df[df['next_step']=='digest']
    return df

def get_and_enhance_input(file_name="/Users/tanxinhuisharon/Downloads/output.csv") -> pd.DataFrame:
    df = pd.read_csv(file_name)
    for index, row in df.iterrows():
        gpt_output_dict = eval(row["chatgpt_output"])
        # {'next_step': 'digest', 'action': 'None', 'summary': 'Justin Birmingham is unable to attend the Ginger Root concert at Warsaw in Greenpoint due to having covid. He is offering his tickets to anyone interested, which he can transfer via the Live Nation app.', 'effort': 'None', 'deadline': 'None', 'constraint': []}
        if 'next_step' in gpt_output_dict:
            df['next_step'] = gpt_output_dict['next_step']
        if 'action' in gpt_output_dict:
            df['action'] = gpt_output_dict['action']
        if 'summary' in gpt_output_dict:
            df['summary'] = gpt_output_dict['summary']
        if 'effort' in gpt_output_dict:
            df['effort'] = gpt_output_dict['effort']
        if 'deadline' in gpt_output_dict:
            df['deadline'] = gpt_output_dict['deadline']
        if 'constraint' in gpt_output_dict:
            df['constraint'] = gpt_output_dict['constraint']
    df['See more'] = False
    return df

if __name__ == '__main__':
    main()