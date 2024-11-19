import argparse
from pathlib import Path
import json

from summarize import handle_summarization
from utils import calculate_file_hash, load_offers_list, offer_path_to_absolute

def parse_args():
    parser = argparse.ArgumentParser(description='Manage the summarization process')
    parser.add_argument('-prompt_path', required=True, type=Path, help='Path to the prompt file')
    parser.add_argument('-output_dir', required=True, type=Path, help='Directory to save the summaries')
    parser.add_argument('-model', required=False, type=str, default='qwen2.5:0.5b', help='Model to use for summarization')
    parser.add_argument('-m', required=False, type=str, default="update", help='Run mode: update (only run for new offers) or overwrite (run for all offers)')
    parser.add_argument('-verbosity', required=False, type=int, default=False, help='Verbose mode: 0 - silent, 1 - print system messages, 2 - print system messages and model outputs')
    parser.add_argument('-offers', required=False, type=int, nargs='+', help='List offers ids to summarize, default is all offers')
    return parser.parse_args()

def main():
    args = parse_args()

    offers_list = load_offers_list()

    for id, offer_details in offers_list:
        hash = offer_details['offer_hash']
        path = offer_details['path']
        output_path = args.output_dir / f'{id}.json'
        if args.m == 'update' and output_path.exists():
            with open(output_path, 'r') as f:
                summary = json.load(f)
                if 'offer_hash' in summary and summary['offer_hash'] == hash and \
                    'model' in summary and summary['model'] == args.model and \
                    'prompt_hash' in summary and summary['prompt_hash'] == calculate_file_hash(args.prompt_path):
                    
                    if (args.verbosity > 0):
                        print(f"Summary for offer {id} already exists and is up to date")
                    continue

        handle_summarization(args.prompt_path, id, offer_path_to_absolute(path), output_path, args.model, verbosity=args.verbosity)
        if (args.verbosity > 0):
            print(f"Summary for offer {id} created")

if __name__ == '__main__':
    main()