from pathlib import Path
import json
import hashlib

def calculate_file_hash(path):
    with open(path, 'rb') as file:
        file_hash = hashlib.sha256(file.read())
    return file_hash.hexdigest()

def save_json(path: Path, data: dict, pretty: bool = True):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as file:
        if pretty:
            json.dump(data, file, indent=4)
        else:
            json.dump(data, file)

def load_json(path: Path):
    with open(path, "r") as file:
        return json.load(file)

