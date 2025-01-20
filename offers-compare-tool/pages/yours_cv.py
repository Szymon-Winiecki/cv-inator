from jinja2 import Template
from data_access import load_usernames, load_generated_cvs,load_html_cv
from data_display import display_job_offer, display_user_form
import streamlit as st
import datetime
import json
from cv_visualisation.generate import generate_cv
from pathlib import Path
import subprocess

def display_page():
    st.title("Your CVs")
    
    usernames = load_usernames()
    user = st.selectbox("Select user", usernames)

    generated_cvs = load_generated_cvs(user)
    for cv in generated_cvs:
        username, template, offer_id = cv.split('_')
        offer_id = offer_id.split('.')[0]
        st.write('Template: ', template)
        st.write('Offer ID: ', offer_id)
        st.download_button(label="Download CV",data=load_html_cv(username, template, offer_id),file_name=cv + '.html',mime="text/html")
    
if __name__ == "__main__":
    display_page()
