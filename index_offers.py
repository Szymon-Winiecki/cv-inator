from pathlib import Path
import json
import datetime
from enum import Enum

from utils import calculate_file_hash

SCRIPT_VERSION = '1.1'

INDEX_PATH = Path('offers') / 'index.json'
OFFERS_DIRS = (
    Path('offers') / 'json',
    )

class Operation(Enum):
    NONE = 0
    ADD = 1
    UPDATE = 2
    REMOVE = 3

def init_index(path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True)

    index = {
        'index_script_version': SCRIPT_VERSION,
        'index_last_update': datetime.datetime.now().isoformat(),
        'offers': {},
        'next_id': 1,
    }

    with open(path, 'w') as f:
        json.dump(index, f, indent=4)

def load_index(path):
    if not path.exists():
        init_index(path)

    with open(path, 'r') as f:
        return json.load(f)
    
def save_index(index, path):
    with open(path, 'w') as f:
        json.dump(index, f, indent=4)
    
def update(index, offer_path):
    if not offer_path.exists():
        return
    
    offer_hash = calculate_file_hash(offer_path)

    matched_offer_id = next((id for id, data in index['offers'].items() if data['offer_hash'] == offer_hash), None)

    if matched_offer_id:
        if index['offers'][matched_offer_id]['path'] != str(offer_path):
            index['offers'][matched_offer_id]['path'] = str(offer_path)
            return (matched_offer_id, Operation.UPDATE)
        return (matched_offer_id, Operation.NONE)
    
    matched_offer_id = index['next_id']
    index['next_id'] += 1
    index['offers'][matched_offer_id] = {
        'offer_hash': offer_hash,
        'path': str(offer_path),
    }
    return (matched_offer_id, Operation.ADD)

def print_stats(stats):
    print(f'Total offers processed: {sum(stats.values())}')
    print(f'Offers added: {stats[Operation.ADD]}')
    print(f'Offers updated: {stats[Operation.UPDATE]}')
    print(f'Offers removed: {stats[Operation.REMOVE]}')
    print(f'Offers unchanged: {stats[Operation.NONE]}')
        

    
def main():
    index = load_index(INDEX_PATH)
    records_to_remove = list(index['offers'].keys())

    stats = {
        Operation.NONE: 0,
        Operation.ADD: 0,
        Operation.UPDATE: 0,
        Operation.REMOVE: 0,
    }

    for offers_dir in OFFERS_DIRS:
        for offer_path in offers_dir.glob('*.json'):
            matched_offer_id, operation = update(index, offer_path)
            stats[operation] += 1
            if operation in (Operation.NONE, Operation.UPDATE):
                records_to_remove.remove(matched_offer_id)

    for id in records_to_remove:
        del index['offers'][id]
        stats[Operation.REMOVE] += 1

    index['index_last_update'] = datetime.datetime.now().isoformat()

    save_index(index, INDEX_PATH)

    print_stats(stats)
    

if __name__ == '__main__':
    main()