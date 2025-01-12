import argparse
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-input_dir', '-i', required=True, type=Path, help='Directory with embeddings files')
    parser.add_argument('-output_dir', '-o', required=True, type=Path, help='Direcotry for saving the output')
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
        ax.annotate(labels[i].name, (embeddings_pca[i, 0], embeddings_pca[i, 1]))
    
    ax.legend()
    plt.savefig(output_path)

def compare_lists(lists):
    similarities = np.zeros((len(lists), len(lists)))

    lists = [ set([l.lower() for l in list]) for list in lists ]

    for a, listA in enumerate(lists):
        for b, listB in enumerate(lists):
            if a == b:
                similarities[a, b] = 1
                continue
            common = len(listA & listB)
            similarities[a, b] = common / len(listB) if len(listB) > 0 else 1
            similarities[b, a] = common / len(listA) if len(listA) > 0 else 1

    return similarities


def main():
    parsed_args = parse_args()

    

    info_files = [f for f in parsed_args.input_dir.iterdir() if f.is_file() and f.suffix == '.json']
    summary_files = []
    embeddings = None
    embedded_fields = []
    model_name = ''

    first_file = True
    for file_ind, info_path in enumerate(info_files):
        info = json.load(open(info_path, 'r'))

        if first_file:
            model_name = info['model']
        elif model_name != info['model']:
            raise ValueError('Different models in the input files')
        
        if first_file:
            embedded_fields = info['embedded_fields']
        elif embedded_fields != info['embedded_fields']:
            raise ValueError('Different embedded fields in the input files')
        
        summary_files.append(info['input_file'])


        embeddings_file = info_path.parent / (info_path.stem.replace('_info', '') + '.npy')
        embedding = np.load(embeddings_file)

        if first_file:
            embeddings = np.zeros((len(info_files), embedding.shape[0], embedding.shape[1]))
            first_file = False
        
        embeddings[file_ind] = embedding

    ###
    # methods of comparison:
    # - embeddings similarity
    # - list compatibility
    ###

    # fields to compare with each method and their weights
    fields_to_compare_with_embeddings = {'job_title': 1, 'job_description': 2, 'requirements': 2, 'benefits': 0.5}
    fields_to_compare_with_list_comp = {'required_skills': 2, 'nice_to_have_skills': 1}

    lists_to_compare = {}
    for field in fields_to_compare_with_list_comp:
        lists_to_compare[field] = []

    for summary_file in summary_files:
        summary = json.load(open(summary_file, 'r'))['offer_summary']
        for field in fields_to_compare_with_list_comp:
            lists_to_compare[field].append(summary[field])


    model = SentenceTransformer(model_name)

    num_offers = embeddings.shape[0]
    num_fields = len(fields_to_compare_with_embeddings) + len(fields_to_compare_with_list_comp)


    partial_similarities = np.zeros((num_fields, num_offers, num_offers))
    similarities = np.zeros((num_offers, num_offers))

    field_ind = 0

    for field in fields_to_compare_with_embeddings:
        partial_similarities[field_ind] = model.similarity(embeddings[:, field_ind], embeddings[:, field_ind])
        similarities += fields_to_compare_with_embeddings[field] * partial_similarities[field_ind]
        field_ind += 1
    
    for field in fields_to_compare_with_list_comp:
        partial_similarities[field_ind] = compare_lists(lists_to_compare[field])
        similarities += fields_to_compare_with_list_comp[field] * partial_similarities[field_ind]
        field_ind += 1

    similarities /= sum(fields_to_compare_with_embeddings.values()) + sum(fields_to_compare_with_list_comp.values())

    concatenated_embeddings = embeddings.reshape((len(info_files), -1))

    output_dir = Path(parsed_args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_similarity(similarities, info_files, output_dir / 'final_similarity_matrix.png')
    plot_similarity(partial_similarities[-2], info_files, output_dir / 'required_skills_similarity_matrix.png')
    plot_pca(embeddings[:, embedded_fields.index('job_description')], info_files, output_dir / 'job_description_pca_plot.png')
    plot_pca(concatenated_embeddings, info_files, output_dir / 'concatenated_pca_plot.png')

if __name__ == '__main__':
    main()
    






    


