import argparse
import pathlib
import json
import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-input_dir', required=True, type=str, help='input directory with summarized offers')
    parser.add_argument('-output_path', required=True, type=str, help='Output path for the comparison results')
    return parser.parse_args()

if __name__ == '__main__':

    parsed_args = parse_args()

    fields_to_compare = ['job_title', 'job_description', 'requirements', 'requiered_skills', 'nice_to_have_skills', 'benefits']
    fields_weights = {'job_title': 1, 'job_description': 2, 'requirements': 2, 'requiered_skills': 2, 'nice_to_have_skills': 1, 'benefits': 0.5}

    input_dir = pathlib.Path(parsed_args.input_dir)

    input_files = [f for f in input_dir.iterdir() if f.is_file() and f.suffix == '.json']

    model = SentenceTransformer("paraphrase-albert-small-v2")
    # model = SentenceTransformer("all-MiniLM-L6-v2")
    MODEL_EMBEDDING_SIZE = 768
    # MODEL_EMBEDDING_SIZE = 384

    embeddings = np.zeros((len(input_files), len(fields_to_compare), MODEL_EMBEDDING_SIZE))

    for file_ind, file in enumerate(input_files):
        offer = json.load(open(file, 'r'))['offer_summary']
        for field_ind, field in enumerate(fields_to_compare):
            text = ", ".join(offer[field]) if type(offer[field]) == list else offer[field]
            embeddings[file_ind, field_ind] = model.encode(text)



    partial_similarities = np.zeros((len(fields_to_compare), len(input_files), len(input_files)))
    similarities = np.zeros((len(input_files), len(input_files)))

    for field_ind, field in enumerate(fields_to_compare):
        partial_similarities[field_ind] = model.similarity(embeddings[:, field_ind], embeddings[:, field_ind])

    for field_ind, field in enumerate(fields_to_compare):
        similarities += fields_weights[field] * partial_similarities[field_ind]

    similarities /= sum(fields_weights.values())

    fig, ax = plt.subplots()
    cax = ax.matshow(similarities, cmap='viridis')
    plt.colorbar(cax)

    ax.set_xticks(np.arange(len(input_files)))
    ax.set_yticks(np.arange(len(input_files)))

    ax.set_xticklabels([f.name for f in input_files])
    ax.set_yticklabels([f.name for f in input_files])

    for i in range(len(input_files)):
        for j in range(len(input_files)):
            text = ax.text(j, i, round(similarities[i, j], 2), ha='center', va='center', color='w')

    plt.savefig(parsed_args.output_path)






    


