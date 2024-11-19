import hashlib

def calculate_file_hash(path):
    with open(path, 'rb') as file:
        file_hash = hashlib.sha256(file.read())
    return file_hash.hexdigest()