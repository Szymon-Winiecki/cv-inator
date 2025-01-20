from jinja2 import Template
from data_access import load_usernames, load_cv_data, load_templates, load_template_path, get_output_path, load_offers, load_offer_path, load_cv_path, load_output_path_cv_generated, load_prompt_cv_path
from data_display import display_job_offer, display_user_form
import streamlit as st
import datetime
import json
from cv_visualisation.generate import generate_cv
from pathlib import Path
import subprocess

def display_page():
    st.title("Generate CV")
    
    is_offer = False
    if "offer" in st.query_params:
        is_offer = True

    usernames = load_usernames()
    username = st.selectbox("Select user", usernames)
    templates = load_templates()
    chosen_template = st.selectbox("Choose template", templates)
    
    template_path = load_template_path(chosen_template)

    cv_output_path = get_output_path(username, chosen_template)

    offers = load_offers()

    template_for_offers = st.checkbox("Make CV for offer", value=is_offer)
    choosed_offer = 0

    if is_offer == False:
        if template_for_offers:
            choosed_offer = st.selectbox("Choose offer", offers, key='offer_key')
    else:
        choosed_offer = st.query_params["offer"].split('.')[0]
        if template_for_offers:
            st.selectbox("Offer", offers, index=offers.index(choosed_offer))

    if st.button("Generate CV"):
        if template_for_offers:
            offer_path = load_offer_path(choosed_offer)
            cv_path = load_cv_path(username)
            output_path = load_output_path_cv_generated(username, choosed_offer)
            prompt_path = load_prompt_cv_path()
            subprocess.run(["python","generate_cv_for_job.py",'-prompt_path', prompt_path, '-offer_path', offer_path, '-profile_path', cv_path, '-output_path', output_path, '-verbosity',str(0)])
            generated_cv = generate_cv(Path(template_path), username, choosed_offer,  Path(cv_output_path))
        else:
            generated_cv = generate_cv(Path(template_path), username, 0,  Path(cv_output_path))
        st.success("CV generated successfully")
        st.download_button(label="Download HTML File",data=generated_cv,file_name="file.html",mime="text/html")

if __name__ == "__main__":
    display_page()
