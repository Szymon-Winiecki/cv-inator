import argparse
from pathlib import Path
import json
import numpy as np
from sentence_transformers import SentenceTransformer


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-input_dir', required=True, type=str, help='Input directory with summarized offers')
    parser.add_argument('-output_dir', required=True, type=str, help='Directory for saving the embeddings')
    parser.add_argument('-output_filename', required=True, type=str, help='Core name for the output files')
    return parser.parse_args()

if __name__ == '__main__':

    parsed_args = parse_args()

    fields_to_compare = ['job_title', 'job_description', 'requirements', 'requiered_skills', 'nice_to_have_skills', 'benefits']
    fields_weights = {'job_title': 1, 'job_description': 2, 'requirements': 2, 'requiered_skills': 2, 'nice_to_have_skills': 1, 'benefits': 0.5}

    input_dir = Path(parsed_args.input_dir)

    input_files = [f for f in input_dir.iterdir() if f.is_file() and f.suffix == '.json']

    model = SentenceTransformer("paraphrase-albert-small-v2")
    # model = SentenceTransformer("all-MiniLM-L6-v2")
    MODEL_EMBEDDING_SIZE = 768
    # MODEL_EMBEDDING_SIZE = 384

    embeddings = np.zeros((len(input_files), len(fields_to_compare), MODEL_EMBEDDING_SIZE))

    for file_ind, file in enumerate(input_files):
        offer = json.load(open(file, 'r'))['offer_summary']
        for field_ind, field in enumerate(fields_to_compare):
            if not field in offer:
                offer[field] = 'N/A'
            text = ", ".join(offer[field]) if type(offer[field]) == list else offer[field]
            embeddings[file_ind, field_ind] = model.encode(text)

    embeddings_info = {
        'fields_to_compare': fields_to_compare,
        'fields_weights': fields_weights,
        'input_files': [str(f) for f in input_files],
        'model': 'paraphrase-albert-small-v2',
    }

    info_path = Path(parsed_args.output_dir) / f'{parsed_args.output_filename}_info.json'
    info_path.parent.mkdir(parents=True, exist_ok=True)
    with open(info_path, 'w') as file:
        file.write(json.dumps(embeddings_info, indent=4))

    embeddings_path = Path(parsed_args.output_dir) / f'{parsed_args.output_filename}.npy'
    np.save(embeddings_path, embeddings)






    


