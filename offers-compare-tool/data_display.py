import streamlit as st
from  datetime import datetime
from pathlib import Path

from data_access import load_offer

def display_job_offer(offer_record):

    offer_id, offer_details = offer_record
    offer_path = Path(offer_details.get("path", ""))

    offer = load_offer(offer_path)

    if offer is None:
        st.write(f"Error loading offer {offer_id}, {offer_details}")
        return
    
    timestamp = offer.get("timestamp", "")
    timestamp = datetime.fromisoformat(timestamp.replace("Z", "")).strftime("%Y-%m-%d %H:%M:%S")
    source_url = offer.get("source", "#")

    offer = offer.get("offer", {})

    st.subheader(f"{offer.get('offer_title', 'Unknown Position')} at {offer.get('company', 'Unknown Company')}")
    # Display job details
    st.write(f"**Location:** {offer.get('location', 'Not specified')}")
    st.write(f"**Salary:** {offer.get('salary', 'Not specified')}")
    st.write(f"**Contract Type:** {offer.get('contract', 'Not specified')}")
    st.write(f"**Experience Level:** {offer.get('experience', 'Not specified')}")
    st.write(f"**Expected Technologies:** {offer.get('expected_technologies', 'Not specified')}")
    st.write(f"**Optional Technologies:** {offer.get('optional_technologies', 'Not specified')}")
    st.write(f"**Posted on:** {timestamp}")

    # Display job offer content and responsibilities
    st.subheader("Job Description")
    st.write(offer.get("offer_content", "No description available"))

    # Display application link
    st.subheader("Original offer Link")
    st.write(f"[Apply here]({source_url})")