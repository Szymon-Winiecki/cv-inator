from pathlib import Path

from cvinatordatamanager.DataServer import DataServer
from cvinatorprocessingtools.SummariesComparator import SummariesComparator

import streamlit as st

PROJECT_ROOT_DIR = Path(__file__).resolve().parents[1]

def init_data_server():
    data_server = DataServer(PROJECT_ROOT_DIR / 'data')
    return data_server

def get_offers():
    data_server = init_data_server()
    offers_ids = data_server.get_offers_ids()
    offers_data = data_server.get_offers_by_ids(offers_ids)
    offers = {id: offers_data[id]['offer'] for id in offers_data}
    for id in offers:
        offers[id]['id'] = id
        offers[id]['similarity'] = 0
    data_server.close()
    return offers

def reset_similarities():
    for offer in st.session_state.offers.values():
        offer['similarity'] = 0

def format_list(items):
    """Format a list of items as an unordered HTML list."""
    if not items:
        return "<p>Not specified</p>"
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


@st.cache_data
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

def diplay_offer_expander(offer):
        title = offer.get("offer_title", "No title provided")
        similarity = offer.get("similarity", "")
        if similarity != "" and similarity != 0 and st.session_state.filtered_ids:
            similarity = rf"""[Similarity: **{similarity:.2f}**]"""
        else:
            similarity = ""
        header = f"{similarity} {title} [id: {offer['id']}]"
        with st.expander(header):  # Expander for each offer
            st.markdown(format_offer_details(offer), unsafe_allow_html=True)
            similar_button_key = f"similar_{offer['id']}"
            if st.button("Show Similar Offers", key=similar_button_key):
                st.session_state.filtered_ids = get_similar_offer_ids(offer["id"], top_n=20)
                st.experimental_rerun()  # Reload the page to show filtered offers
            st.markdown('<a href="/generate_cv/?offer={}" target="_self">Generate CV for that offer</a>'.format(offer["id"]), unsafe_allow_html=True)


def get_similar_offer_ids(offer_id, top_n=10):
    data_server = init_data_server()

    selected_offer_embedding_id = data_server.get_newest_embedding_id_by_offer_id(offer_id)

    # get all embeddings ids
    other_embeddings_ids = data_server.get_embeddings_ids()

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

    # get the most similar offers to the first one
    most_similar = summaries_comparator.get_most_similar_summaries(selected_offer_embedding_id, other_embeddings_ids, top_n=top_n)

    # print results
    print(f"Most similar offers to the offer with id {offer_id}:")
    print(most_similar)

    offers_ids = data_server.get_offers_ids_by_embeddings_ids(list(most_similar.keys()))

    most_similar_offers = {offers_ids[emb_id] : most_similar[emb_id] for emb_id in most_similar}

    for offer_id in most_similar_offers:
        st.session_state.offers[offer_id]['similarity'] = most_similar_offers[offer_id]

    data_server.close()
    return list(most_similar_offers.keys())


def display_page():
    st.set_page_config(layout="wide")

    st.title("Job Offers")

    if "offers" not in st.session_state:
        st.session_state.offers = get_offers()

    # State to track filtered offer IDs
    if "filtered_ids" not in st.session_state:
        st.session_state.filtered_ids = None

    # Filters
    st.sidebar.header("Search Filters")
    search_query = st.sidebar.text_input("Search by Title or Company", "")
    location_filter = st.sidebar.text_input("Filter by Location", "")
    experience_filter = st.sidebar.selectbox("Filter by Experience", ["", "junior", "mid", "senior"])
    contract_filter = st.sidebar.text_input("Filter by Contract Type", "")

    order_by = st.sidebar.selectbox("Order by", ["id", "similarity", "offer_title"])
    order_order = st.sidebar.selectbox("Order", ["asc", "desc"])

    # Filter offers based on inputs
    filtered_offers = []
    for offer in st.session_state.offers.values():
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

    # Order offers
    filtered_offers = sorted(filtered_offers, key=lambda x: x.get(order_by, 0), reverse=order_order == "desc")


    offers_per_page = st.sidebar.number_input("Offers per page", 10, 500, 20, step=10)
    page_number = st.sidebar.number_input("Page number", 1, max(1, len(filtered_offers) // offers_per_page + 1), 1)

    
    # Display offers with expanders and similar offer buttons
    if filtered_offers:
        for i, offer in enumerate(filtered_offers[page_number * offers_per_page - offers_per_page : min(page_number * offers_per_page, len(filtered_offers))]):
            diplay_offer_expander(offer)
    else:
        st.write("No offers match your criteria.")

    st.write(f"Page {page_number} of {max(1, len(filtered_offers) // offers_per_page + 1)}")

    # Reset filter button
    if st.session_state.filtered_ids:
        if st.button("Reset Filters"):
            st.session_state.filtered_ids = None
            reset_similarities()
            st.experimental_rerun()  # Reload the page to show all offers


if __name__ == "__main__":
    display_page()
