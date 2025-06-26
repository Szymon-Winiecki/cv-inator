import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import os

PROJECT_ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_SERVER_DIR = PROJECT_ROOT_DIR / "data"
OFFERS_INDEX_PATH = DATA_SERVER_DIR / "offers"
COMPARISON_RECORDS_DIR = PROJECT_ROOT_DIR / "local" / "human_comparisons" / "offers_similarity"
CV_DATA_DIR = PROJECT_ROOT_DIR / "user_data" / "users_cv_data"
CV_GEN_DIR = PROJECT_ROOT_DIR / "generated" / "users_cv_data_generated"
HTML_TEMPLATES_DIR = PROJECT_ROOT_DIR / "cmd_tools" / "cv_visualisation" / "templates"
GENERATED_CV_DIR = PROJECT_ROOT_DIR / "generated" / "generated_cv_html"

@st.cache_data
def load_offers_list():
    paths =  [path for path in OFFERS_INDEX_PATH.glob("*.json")]
    offers_data = [(i, value) for i, value in enumerate(paths)]

    return offers_data

@st.cache_data
def load_offer(offer_path):
    full_path = PROJECT_ROOT_DIR / offer_path

    if not full_path.exists():
        return None
    
    with open(full_path, "r", encoding="utf8") as file:
        return json.load(file)

def load_usernames():
    return [path.stem for path in CV_DATA_DIR.glob("*.json")]

def load_templates():
    return [path.stem for path in HTML_TEMPLATES_DIR.glob("*.html")]

def load_offers():
    return [path.stem for path in OFFERS_INDEX_PATH.glob("*.json")]

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

def save_cv_data(username, data):
    path = CV_DATA_DIR / f"{username}.json"

    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    with open(path, "w") as file:
        json.dump(data, file, indent=4)
        return True
    return False

def remove_comparison_record(username, index):
    path = COMPARISON_RECORDS_DIR / f"{username}.json"

    if not path.exists():
        return
    
    with open(path, "r") as file:
        records = json.load(file)

    del records[index]

    with open(path, "w") as file:
        json.dump(records, file)
    
def load_cv_data(username, offer_id):
    if offer_id == 0:
        full_path = CV_DATA_DIR / f"{username}.json"
    else:
        full_path = CV_GEN_DIR / f"{username}_{offer_id}.json"
    
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            data = json.load(f)
            if data is not None:
                return data
    data = {    
        "profile": {
        "personal_info": {},
        "tech_stack": [],
        "soft_stack": [],
        "education": [],
        "work_experience": [],
        "projects": [],
        "certifications": [],
        "languages": [],
        "about_me": ""
            }
    }
    return data

def load_template_path(template):
    return HTML_TEMPLATES_DIR / f"{template}.html"

def get_output_path(username, template, offer_id):
    return PROJECT_ROOT_DIR / "generated_cv_html" / f"{username}_{template}_{offer_id}.html"

def get_data_directory():
    return DATA_SERVER_DIR / "offers"

def get_database_directory():
    return DATA_SERVER_DIR

def load_offer_path(offer_id):
    return DATA_SERVER_DIR / "offers" / f"{offer_id}.json"

def load_cv_path(username):
    return PROJECT_ROOT_DIR / "users_cv_data" / f"{username}.json"

def load_prompt_cv_path():
    return PROJECT_ROOT_DIR / "prompts" / "cv_generation" / "prompt_pack_01.json"

def load_output_path_cv_generated(username, offer_id):
    return PROJECT_ROOT_DIR / "generated" / "users_cv_data_generated" / f"{username}_{offer_id}.json"

def create_user(username):
    path = CV_DATA_DIR / f"{username}.json"
    data = {    
        "profile": {
        "personal_info": {},
        "tech_stack": [],
        "soft_stack": [],
        "education": [],
        "work_experience": [],
        "projects": [],
        "certifications": [],
        "languages": [],
        "about_me": ""
            }
    }
    with open(path, "w") as file:
        json.dump(data, file, indent=4)

def load_generated_cvs(username):
    return [path.stem for path in GENERATED_CV_DIR.glob(f"{username}_*.html")]

def load_html_cv(username, template, offer):
    path = GENERATED_CV_DIR / f"{username}_{template}_{offer}.html"
    with open(path, "r") as file:
        return file.read()
    