import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
import pandas as pd
import gpt_calls
import asyncio

# Globals

def main():
    st.set_page_config(page_title="Email Crawler Demo", page_icon=":envelope:", layout="wide")
    st.header("Welcome to the Email Crawler.")
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
        
        # df2 = get_digest_list()
        # table2 = st.data_editor(df2)
        # selected_indices = table2[table2['See more'] == True].index.tolist()
        # if selected_indices:
        #     st.session_state.selected_row2 = df2.iloc[selected_indices[0]]
        #     st.session_state.show_more2 = True
        # else:
        #     st.session_state.show_more2 = False  
    
    with col2:
        if st.session_state.show_more:
            st.subheader("Take action")
            if st.session_state.selected_row['summary']:
                st.write("**Description**")
                st.write(st.session_state.selected_row['summary'])
            
            if st.session_state.selected_row['action']:
                st.write("**Suggested action**")
                st.write(st.session_state.selected_row['action'])
            
            if st.session_state.selected_row['deadline']:
                st.write("**Deadline**")
                st.write(st.session_state.selected_row['deadline'])

            if st.session_state.selected_row['constraint']:
                st.write("**Take note**")
                constraint_list = eval(st.session_state.selected_row['constraint'])
                for constraint in constraint_list:
                    st.write(f" - {constraint}")
            
            if st.session_state.selected_row['email_link']:
                st.button(":arrow_upper_right: View in Gmail")

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
    df = df[df['is_todo']=='Y']
    return df

def get_and_enhance_input(file_name="/Users/tanxinhuisharon/Documents/PythonProjects/email-crawler/email-crawler/data.csv") -> pd.DataFrame:
    df = pd.read_csv(file_name)
    df['See more'] = False
    return df

if __name__ == '__main__':
    main()