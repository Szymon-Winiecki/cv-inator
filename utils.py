import hashlib
from pathlib import Path
import json
from datetime import datetime

PROJECT_ROOT_DIR = Path(__file__).resolve().parents[0]

OFFERS_INDEX_PATH = PROJECT_ROOT_DIR / "offers" / "index.json" 
COMPARISON_RECORDS_DIR = PROJECT_ROOT_DIR / "human_comparisons" / "offers_similarity"

def load_offers_list():
    path = OFFERS_INDEX_PATH

    if not path.exists():
        return []
    
    with open(path, "r") as file:
        offers_index = json.load(file)
    
    offers = list(offers_index.get("offers", {}).items())

    return offers

def load_offer(offer_path):
    full_path = PROJECT_ROOT_DIR / offer_path

    if not full_path.exists():
        return None
    
    with open(full_path, "r", encoding="utf8") as file:
        return json.load(file)
    
def offer_path_to_absolute(offer_path):
    return PROJECT_ROOT_DIR / offer_path

def calculate_file_hash(path):
    with open(path, 'rb') as file:
        file_hash = hashlib.sha256(file.read())
    return file_hash.hexdigest()