import argparse
from pathlib import Path
import json

from OffersComparator import OffersComparator


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-input_dir', '-i', required=True, type=Path, help='Directory with embeddings files')
    parser.add_argument('-output_dir', '-o', required=True, type=Path, help='Direcotry for saving the output')
    parser.add_argument('-to_offer', '-to', type=int, default=-1, help='Index of the offer to compare with others')
    return parser.parse_args()




def main():
    parsed_args = parse_args()

    
    ###
    # methods of comparison:
    # - embeddings similarity
    # - list compatibility
    ###

    # fields to compare with each method and their weights
    fields_to_compare_with_embeddings = {'job_title': 1, 'job_description': 2, 'requirements': 2, 'benefits': 0.5}
    fields_to_compare_with_list_comp = {'required_skills': 2, 'nice_to_have_skills': 1}

    comparator = OffersComparator(parsed_args.input_dir, fields_to_compare_with_embeddings, fields_to_compare_with_list_comp)
                                  
    # similarities, partial_similarities = comparator.calc_similarity(to_offer=parsed_args.to_offer)

    # concatenated_embeddings = comparator.calc_concatenated_embeddings()

    # output_dir = Path(parsed_args.output_dir)
    # output_dir.mkdir(parents=True, exist_ok=True)

    # comparator.plot_similarity(similarities, output_dir / 'final_similarity_matrix.png', to_offer=parsed_args.to_offer)
    # comparator.plot_similarity(partial_similarities[-2], output_dir / 'required_skills_similarity_matrix.png', to_offer=parsed_args.to_offer)
    # comparator.plot_pca(comparator.embeddings[:, 1], output_dir / 'job_description_pca_plot.png')
    # comparator.plot_pca(concatenated_embeddings, output_dir / 'concatenated_pca_plot.png')

    most_similar = comparator.get_most_similar(to_offer=parsed_args.to_offer)

    
    

if __name__ == '__main__':
    main()
    






    


