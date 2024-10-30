import argparse
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-input_path', required=True, type=str, help='Path to the embeddings file')
    parser.add_argument('-output_dir', required=True, type=str, help='Direcotry for saving the output')
    return parser.parse_args()

def plot_similarity(similarities, labels, output_path):
    fig, ax = plt.subplots()
    cax = ax.matshow(similarities, cmap='viridis')
    plt.colorbar(cax)

    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))

    ax.set_xticklabels([f.name for f in labels])
    ax.set_yticklabels([f.name for f in labels])

    for i in range(len(labels)):
        for j in range(len(labels)):
            text = ax.text(j, i, round(similarities[i, j], 2), ha='center', va='center', color='w')

    plt.savefig(output_path)

def plot_pca(embeddings, labels, output_path):
    pca = PCA(n_components=2)
    embeddings_pca = pca.fit_transform(embeddings)

    fig, ax = plt.subplots()
    for i in range(len(labels)):
        ax.scatter(embeddings_pca[i, 0], embeddings_pca[i, 1], label=labels[i].name)
    
    ax.legend()
    plt.savefig(output_path)

if __name__ == '__main__':

    parsed_args = parse_args()

    embeddings = np.load(parsed_args.input_path)

    info_file = parsed_args.input_path.replace('.npy', '_info.json')
    embeddings_info = json.load(open(info_file, 'r'))

    fields_to_compare = embeddings_info['fields_to_compare']
    fields_weights = embeddings_info['fields_weights']
    input_files = [Path(f) for f in embeddings_info['input_files']]
    model = SentenceTransformer(embeddings_info['model'])



    partial_similarities = np.zeros((len(fields_to_compare), len(input_files), len(input_files)))
    similarities = np.zeros((len(input_files), len(input_files)))

    for field_ind, field in enumerate(fields_to_compare):
        partial_similarities[field_ind] = model.similarity(embeddings[:, field_ind], embeddings[:, field_ind])

    for field_ind, field in enumerate(fields_to_compare):
        similarities += fields_weights[field] * partial_similarities[field_ind]

    similarities /= sum(fields_weights.values())

    output_dir = Path(parsed_args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_similarity(similarities, input_files, output_dir / 'final_similarity_matrix.png')
    plot_pca(embeddings[:, fields_to_compare.index('job_description')], input_files, output_dir / 'job_description_pca_plot.png')






    


