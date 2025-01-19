import streamlit as st
import os
import json
from cvinatordatamanager.DataServer import DataServer

from  cvinatorprocessingtools.SummariesComparator import SummariesComparator

# Path to the directory containing JSON files
DATA_DIRECTORY = "../data/offers"

def load_offers(data_directory):
    offers = []
    for filename in os.listdir(data_directory):
        if filename.endswith(".json"):
            with open(os.path.join(data_directory, filename), "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    offer = data.get("offer", {})
                    offer["id"] = filename  # Add the filename as the ID
                    offers.append(offer)
                except json.JSONDecodeError:
                    st.warning(f"Failed to parse {filename}")
    return offers

def get_similar_offer_ids(offer_id):
    data_server = DataServer('../data', create_if_not_exists=False)
    offer_id=offer_id.replace('.json', '')
    # define how comparation should be done
    # specify which features of the offer (summary in fact) should be compared and how
    comparation_scheme = {
        'job_title': {
            'method': 'embedding',  # compare embeddings of this field with SBERT built-in simmilarity measure
            'weight': 1.0           # importance of the field in the final similarity
        },
        'job_description': {
            'method': 'embedding',
            'weight': 2.0
        },
        'requirements': {
            'method': 'embedding',
            'weight': 1.0
        },
        'required_skills': {
            'method': 'list',   # compare lists of strings by the number of common elements (how many of the required skills are the same)
            'weight': 2.0
        }
    }

    # create comparator object
    summaries_comparator = SummariesComparator(data_server, comparation_scheme)

    # get all embeddings ids
    embeddings_ids = data_server.get_embeddings_ids()

    # get the most similar offers to the first one
    most_similar = summaries_comparator.get_most_similar_summaries(embeddings_ids[int(offer_id)-1], embeddings_ids)

    # print results
    print(f"Most similar offers to the offer with id {offer_id}:")
    print(most_similar)

    # get 3 most similar offers
    most_similar_emb_ids = list(most_similar.keys())[:10]
    #adding .json to every id
    most_similar_emb_ids = [str(emb_id)+'.json' for emb_id in most_similar_emb_ids]
    return most_similar_emb_ids

def format_list(items):
    """Format a list of items as an unordered HTML list."""
    if not items:
        return "<p>Not specified</p>"
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"

def format_offer_details(offer):
    """Format detailed information of a single offer with visual separation."""
    company = offer.get("company", "No company provided")
    contract = offer.get("contract", "Not specified")
    location = offer.get("location", "Location not specified")
    experience = offer.get("experience", "Not specified")
    about = offer.get("about", "No description provided")
    technologies = format_list(offer.get("expected_technologies", []))
    requirements = format_list(offer.get("requirements", []))
    duties = format_list(offer.get("duties", []))

    return f"""
    <div style="padding: 10px; border: 2px solid #ddd; margin-bottom: 15px; border-radius: 10px;">
        <h4 style="color: #2e7d32; margin-bottom: 10px;">Company: {company}</h4>
        <p><strong>Contract Type:</strong> {contract}</p>
        <p><strong>Location:</strong> {location}</p>
        <p><strong>Experience:</strong> {experience}</p>
        <hr style="border: 1px solid #ddd;" />
        <h5 style="color: #1565c0;">About the Job</h5>
        <p>{about}</p>
        <hr style="border: 1px solid #ddd;" />
        <h5 style="color: #6a1b9a;">Expected Technologies</h5>
        {technologies}
        <hr style="border: 1px solid #ddd;" />
        <h5 style="color: #d32f2f;">Requirements</h5>
        {requirements}
        <hr style="border: 1px solid #ddd;" />
        <h5 style="color: #0288d1;">Duties</h5>
        {duties}
    </div>
    """

def display_page():
    """Displays the job offers page."""
    st.title("Job Offers")

    # Load offers
    offers = load_offers(DATA_DIRECTORY)

    # State to track filtered offer IDs
    if "filtered_ids" not in st.session_state:
        st.session_state.filtered_ids = None

    # Filters
    st.sidebar.header("Search Filters")
    search_query = st.sidebar.text_input("Search by Title or Company", "")
    location_filter = st.sidebar.text_input("Filter by Location", "")
    experience_filter = st.sidebar.selectbox("Filter by Experience", ["", "junior", "mid", "senior"])
    contract_filter = st.sidebar.text_input("Filter by Contract Type", "")

    # Filter offers based on inputs
    filtered_offers = []
    for offer in offers:
        if st.session_state.filtered_ids and offer["id"] not in st.session_state.filtered_ids:
            continue
        if search_query and search_query.lower() not in (offer.get("offer_title", "").lower() + offer.get("company", "").lower()):
            continue
        if location_filter and location_filter.lower() not in offer.get("location", "").lower():
            continue
        if experience_filter and experience_filter.lower() != offer.get("experience", "").lower():
            continue
        if contract_filter and contract_filter.lower() not in offer.get("contract", "").lower():
            continue
        filtered_offers.append(offer)

    # Display offers with expanders and similar offer buttons
    if filtered_offers:
        for offer in filtered_offers:
            title = offer.get("offer_title", "No title provided")
            with st.expander(title):  # Expander for each offer
                st.markdown(format_offer_details(offer), unsafe_allow_html=True)
                similar_button_key = f"similar_{offer['id']}"
                if st.button("Show Similar Offers", key=similar_button_key):
                    st.session_state.filtered_ids = get_similar_offer_ids(offer["id"])
                    st.experimental_rerun()  # Reload the page to show filtered offers
    else:
        st.write("No offers match your criteria.")

    # Reset filter button
    if st.session_state.filtered_ids:
        if st.button("Reset Filters"):
            st.session_state.filtered_ids = None
            st.experimental_rerun()  # Reload the page to show all offers

# Use this function to test the page independently if needed
if __name__ == "__main__":
    display_page()
