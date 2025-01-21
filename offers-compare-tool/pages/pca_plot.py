from cvinatordatamanager.DataServer import DataServer
from cvinatorprocessingtools.SummariesComparator import SummariesComparator

from sklearn.decomposition import PCA

import pandas as pd

import streamlit as st

def init_data_server():
    data_server = DataServer('../data')
    return data_server

def get_concatenated_embeddings(data_server):
    embeddings_ids = data_server.get_embeddings_ids()

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
    comparator = SummariesComparator(data_server, comparation_scheme)

    embeddings, embeddings_ids = comparator.get_concatenated_embeddings(embeddings_ids)
    return embeddings, embeddings_ids

def calc_pca(embeddings):
    pca = PCA(n_components=2)
    pca_embeddings = pca.fit_transform(embeddings)
    return pca_embeddings

# return 2d pca of embeddings and their ids in streamlit scatter plot compatible format
def get_plot_data():
    data_server = init_data_server()
    embeddings, embeddings_ids = get_concatenated_embeddings(data_server)
    pca_embeddings = calc_pca(embeddings)
    data_server.close()
    pca_embeddings = pd.DataFrame(pca_embeddings, columns=['x', 'y'])
    pca_embeddings['id'] = embeddings_ids
    pca_embeddings['selected'] = False
    return pca_embeddings

def get_offers_data(embeddings_ids):
    data_server = init_data_server()
    offers_data_ids = data_server.get_offers_ids_by_embeddings_ids(embeddings_ids)
    offers_data = data_server.get_offers_by_ids([offers_data_ids[emb_id] for emb_id in offers_data_ids])

    emb_id_to_offer = {emb_id: offers_data[offers_data_ids[emb_id]]['offer'] for emb_id in offers_data_ids}
    for emb_id in emb_id_to_offer:
        emb_id_to_offer[emb_id]['id'] = offers_data_ids[emb_id]

    data_server.close()
    return emb_id_to_offer

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

def diplay_offer_expander(offer):
        title = offer.get("offer_title", "No title provided")
        with st.expander(f"{title} [{offer['id']}]"):  # Expander for each offer
            st.markdown(format_offer_details(offer), unsafe_allow_html=True)


def display_page():
    st.set_page_config(layout="wide")

    st.title("PCA Plot")

    st.write("Select offers to highlight them on the plot")

    if 'plot_data' not in st.session_state:
        st.session_state.plot_data = get_plot_data()
        st.session_state.offers = get_offers_data(st.session_state.plot_data['id'].to_list()) # emb id to offer dict
        st.session_state.list_data = st.session_state.plot_data.copy()['id']

        st.session_state.list_data = st.session_state.list_data.to_frame()
        st.session_state.list_data['title'] = st.session_state.list_data['id'].apply(lambda id: st.session_state.offers[id]['offer_title'])


    left, right = st.columns(2)

    event = right.dataframe(st.session_state.list_data, on_select='rerun', selection_mode='multi-row', hide_index=True)

    selected_index = st.session_state.list_data.loc[event.selection.rows]['id'].to_list()
    st.session_state.plot_data['selected'] = False
    st.session_state.plot_data.loc[st.session_state.plot_data['id'].isin(selected_index), 'selected'] = True

    left.scatter_chart(st.session_state.plot_data, x='x', y='y', color='selected', height=600)

    for id in selected_index:
        diplay_offer_expander(st.session_state.offers[id])

display_page()