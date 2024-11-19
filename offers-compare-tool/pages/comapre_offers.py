import streamlit as st
import random

from data_access import load_offers_list, load_offer, add_comparison_record
from data_display import display_job_offer

def get_random_job_offers(job_offers, n=3):
    return random.sample(job_offers, n)

def choose_new_offers(job_offers):
    st.session_state.displayed_offers = get_random_job_offers(job_offers, 3)
    st.session_state.selected_offer = 1

def select_offer(side):
    if side == "LEFT":
        st.session_state.selected_offer = 0
    elif side == "RIGHT":
        st.session_state.selected_offer = 2

def accept():
    username = st.session_state.username
    main_offer = st.session_state.displayed_offers[1]
    compared_offers = [st.session_state.displayed_offers[0], st.session_state.displayed_offers[2]]
    selected_offer = 0 if st.session_state.selected_offer == 0 else 1

    add_comparison_record(username, main_offer, compared_offers, selected_offer)

    choose_new_offers(load_offers_list())


def display_page():
    st.set_page_config(layout="wide")

    job_offers = load_offers_list()

    if "selected_offer" not in st.session_state:
        st.session_state.selected_offer = 1

    st.title("Job Offers Comparison Tool")

    st.write("Instructions:")
    st.write("1. Enter your name.")
    st.write("2. Click on the LEFT or RIGHT button to select the offer that is more similar to the one in the middle.")
    st.write("3. Click on the ACCEPT button to save the comparison and get a new set of offers.")
    st.write("4. Repeat the process as long as you want.")

    st.write("Please select the offer that is more similar to the one in the middle from the perspective of the job seeker.")

    username = st.text_input("Enter your name", key="username")

    if len(job_offers) > 2:

        if "displayed_offers" not in st.session_state:
            choose_new_offers(job_offers)

        columns = st.columns(3)

        with columns[0]:
            type = "primary" if st.session_state.selected_offer == 0 else "secondary"
            st.button("LEFT", on_click=select_offer, args=("LEFT",), type=type, disabled=not username)
            display_job_offer(st.session_state.displayed_offers[0])

        with columns[1]:
            st.button("ACCEPT", type="secondary", on_click=accept, disabled=st.session_state.selected_offer == 1)
            display_job_offer(st.session_state.displayed_offers[1])

        with columns[2]:
            type = "primary" if st.session_state.selected_offer == 2 else "secondary"
            st.button("RIGHT", on_click=select_offer, args=("RIGHT",), type=type, disabled=not username)
            display_job_offer(st.session_state.displayed_offers[2])
            

    else:
        st.write("Not enaught job offers to compare.")

if __name__ == "__main__":
    display_page()
