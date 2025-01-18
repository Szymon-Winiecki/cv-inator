import argparse
from pathlib import Path
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import datetime
from utils import calculate_file_hash


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize the job offer')
    parser.add_argument('-input_dir', '-i', required=True, type=str, help='Input directory with summarized offers')
    parser.add_argument('-output_dir', '-o', required=True, type=str, help='Directory for saving the embeddings')
    parser.add_argument('-output_filename', required=False, default='embedding', type=str, help='Core name for the output files')
    parser.add_argument('-model', required=False, type=str, default='paraphrase-albert-small-v2', help='Model to use for embeddings')
    parser.add_argument('-model_embedding_size', required=False, type=int, default=768, help='Size of the model embeddings')
    parser.add_argument('-verbosity', '-v', required=False, type=int, default=0, help='Verbose mode: 0 - silent, 1 - print system messages, 2 - print system messages and model outputs')
    return parser.parse_args()

def calc_embedding(summary, fields_to_embed, model="paraphrase-albert-small-v2", model_embedding_size=768):  

    model = SentenceTransformer(model)

    embeddings = np.zeros((len(fields_to_embed), model_embedding_size))

    for field_ind, field in enumerate(fields_to_embed):
        if not field in summary:
            summary[field] = 'N/A'
        text = ", ".join(summary[field]) if type(summary[field]) == list else summary[field]
        embeddings[field_ind] = model.encode(text)

    return embeddings

def embed_summary(summary_path, output_path, fields_to_embed, model="paraphrase-albert-small-v2", model_embedding_size=768, verbosity=0):
    if not isinstance(summary_path, Path):
        summary_path = Path(summary_path)
    
    summary = json.load(open(summary_path, 'r'))['offer_summary']

    embeddings = calc_embedding(summary, fields_to_embed, model, model_embedding_size)

    embeddings_info = {
        'embedded_fields': fields_to_embed,
        'input_file': str(summary_path),
        'input_file_hash': calculate_file_hash(summary_path),
        'model': model,
        'timestamp': datetime.now().isoformat(' ')
    }

    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True)

    info_path = output_path.parent / f'{output_path.stem}_info.json'
    with open(info_path, 'w') as file:
        file.write(json.dumps(embeddings_info, indent=4))

    embeddings_path = output_path.parent / f'{output_path.stem}.npy'
    np.save(embeddings_path, embeddings)

    if verbosity > 0:
        print(f'Embeddings for {summary_path} saved to {embeddings_path}')

if __name__ == '__main__':

    parsed_args = parse_args()

    fields_to_embed = ['job_title', 'job_description', 'requirements', 'required_skills', 'nice_to_have_skills', 'benefits']

    input_dir = Path(parsed_args.input_dir)

    input_files = [f for f in input_dir.iterdir() if f.is_file() and f.suffix == '.json']


    for input_file in input_files:
        output_path = Path(parsed_args.output_dir) / f'{parsed_args.output_filename}_{input_file.stem}'
        embed_summary(input_file, output_path, fields_to_embed, parsed_args.model, parsed_args.model_embedding_size, verbosity=parsed_args.verbosity)






    


