import streamlit as st
from pathlib import Path
import json

from data_access import load_offers_list, load_offer, load_comparisons, load_usernames, remove_comparison_record
from data_display import display_job_offer
 
def display_comparison(comparison, index):
    with st.expander(f"Comparison {comparison['main_offer'][0]} vs {comparison['compared_offers'][0][0]} and {comparison['compared_offers'][1][0]} [{comparison['timestamp']}]"):

        if st.button("Delete comparison", key=f'delete_{index}'):
            remove_comparison_record(comparison['username'], index)
            st.rerun()

        main_tab, more_similar_tab, less_similar_tab = st.tabs(["Main offer", "More similar offer", "Less similar offer"])

        with main_tab:
            display_job_offer(comparison['main_offer'])
        
        with more_similar_tab:
            display_job_offer(comparison['compared_offers'][comparison['selected_offer']])

        with less_similar_tab:
            display_job_offer(comparison['compared_offers'][1 - comparison['selected_offer']])

        

def display_page():
    st.title("Manage Comparisons")
    
    usernames = load_usernames()
    username = st.selectbox("Select user", usernames)
    
    comparisons = load_comparisons(username)
    
    st.write(f"User {username} has made {len(comparisons)} comparisons")
    
    for id, comparison in enumerate(comparisons):
        display_comparison(comparison, id)

if __name__ == "__main__":
    display_page()