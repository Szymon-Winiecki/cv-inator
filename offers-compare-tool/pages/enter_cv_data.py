from data_access import load_offers_list, load_offer, add_comparison_record, load_comparisons, load_usernames, remove_comparison_record, save_cv_data, load_cv_data
from data_display import display_job_offer, display_user_form
import streamlit as st
import datetime
import json

def display_page():
    st.title("Make CV")
    
    usernames = load_usernames()
    username = st.selectbox("Select user", usernames)
    data = load_cv_data(username, 0)
    user_data = display_user_form(username, data)

    if user_data is not None:
        if save_cv_data(username, user_data):
            st.success("Form submitted and data saved!")
            
if __name__ == "__main__":
    display_page()
