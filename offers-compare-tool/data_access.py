import streamlit as st
from pathlib import Path
import json
from datetime import datetime

PROJECT_ROOT_DIR = Path(__file__).resolve().parents[1]

# Path to the job offers index file
OFFERS_INDEX_PATH = PROJECT_ROOT_DIR / "offers" / "index.json" 
COMPARISON_RECORDS_DIR = PROJECT_ROOT_DIR / "human_comparisons" / "offers_similarity"

@st.cache_data
def load_offers_list():
    path = OFFERS_INDEX_PATH

    if not path.exists():
        return []
    
    with open(path, "r") as file:
        offers_index = json.load(file)
    
    offers = list(offers_index.get("offers", {}).items())

    return offers

@st.cache_data
def load_offer(offer_path):
    full_path = PROJECT_ROOT_DIR / offer_path

    if not full_path.exists():
        return None
    
    with open(full_path, "r", encoding="utf8") as file:
        return json.load(file)

def load_usernames():
    return [path.stem for path in COMPARISON_RECORDS_DIR.glob("*.json")]

def load_comparisons(username):
    path = COMPARISON_RECORDS_DIR / f"{username}.json"
    if not path.exists():
        return []
    
    with open(path, "r") as file:
        return json.load(file)
    
def add_comparison_record(username, main_offer, compared_offers, selected_offer):

    record = {
        "main_offer": main_offer,
        "compared_offers": compared_offers,
        "selected_offer": selected_offer,
        "username": username,
        "timestamp": datetime.now().isoformat()
    }

    path = COMPARISON_RECORDS_DIR / f"{username}.json"

    records = []

    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    elif path.exists():
        with open(path) as file:
            records = json.load(file)

    records.append(record)

    with open(path, "w") as file:
        json.dump(records, file)

def remove_comparison_record(username, index):
    path = COMPARISON_RECORDS_DIR / f"{username}.json"

    if not path.exists():
        return
    
    with open(path, "r") as file:
        records = json.load(file)

    del records[index]

    with open(path, "w") as file:
        json.dump(records, file)