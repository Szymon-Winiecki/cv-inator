from data_access import load_usernames, save_cv_data, load_cv_data, create_user
from data_display import display_user_form
import streamlit as st

def display_page():
    st.title("Make CV")

    username = st.text_input("Enter your name", key="username")
    if st.button("Add new user"):
        if username:
            if username not in load_usernames():
                create_user(username)

    usernames = load_usernames()
    username = st.selectbox("Select user", usernames)
    data = load_cv_data(username, 0)
    user_data = display_user_form(username, data)

    if user_data is not None:
        if save_cv_data(username, user_data):
            st.success("Form submitted and data saved!")
            
if __name__ == "__main__":
    display_page()
