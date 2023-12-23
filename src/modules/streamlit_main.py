import streamlit as st
import pandas as pd
import requests

# Globals

def main():
    st.set_page_config(page_title="Email Crawler Demo", page_icon=":envelope:", layout="wide")
    # TODO: Modify to track authentication status
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = True
    if 'show_more' not in st.session_state:
        st.session_state['show_more'] = False

    col_a, col_b = st.columns([1, 13])
    with col_a:
        st.image('./Assets/logo-no-bg.png', width=75)
    with col_b:
        st.header("Swiftly: Spend time on people and passions - not email")

    response = requests.get('http://127.0.0.1:5000/healthcheck')
    if response.status_code == 200:
        st.write(response.text)

    col1, col2 = st.columns([3.5, 1.5], gap="large")
    
    with col1: 
        st.subheader("To Do")
        st.write("There are messages that require an action from you soon.")
        # if st.button("Call GPT-4"):
        #     asyncio.run(call_gpt_with_query(table))

        df = get_to_do_list()
        df_for_display = df[['summary', 'effort', 'See more']]
        table = st.data_editor(df_for_display)
        selected_indices = table[table['See more'] == True].index.tolist()
        print(st.session_state)
        if selected_indices:
            st.session_state.selected_row = df.iloc[selected_indices[0]]  # Always take the first selected row
            st.session_state.show_more = True
        else:
            st.session_state.show_more = False

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
            
            st.button(":arrow_upper_right: View in Gmail")

            if st.session_state.selected_row['action']:
                st.button(":calendar: Add to calendar")

def get_to_do_list() -> pd.DataFrame:
    # Make a dataframe with columns Done, Task, From, Effort, Urgency, Source
    df = get_and_enhance_input()

    return df

def get_and_enhance_input(file_name="data/output.csv") -> pd.DataFrame:
    df = pd.read_csv(file_name)
    for index, row in df.iterrows():
        gpt_output_dict = eval(row["chatgpt_output"])
        for key in ['next_step', 'action', 'summary', 'effort', 'deadline', 'constraint']:
            if key in gpt_output_dict:
                df.at[index, key] = gpt_output_dict[key]
    df['See more'] = False
    return df

if __name__ == '__main__':
    main()