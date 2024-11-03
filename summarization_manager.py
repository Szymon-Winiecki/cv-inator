import argparse
import hashlib
from pathlib import Path
import json

from summarize import handle_summarization, calculate_file_hash

def parse_args():
    parser = argparse.ArgumentParser(description='Manage the summarization process')
    parser.add_argument('-prompt_path', required=True, type=Path, help='Path to the prompt file')
    parser.add_argument('-offer_dirs', required=True, type=Path, nargs='+', help='List of directories containing offer files')
    parser.add_argument('-output_dirs', required=True, type=Path, nargs='+', help='List of directories to save the summaries must match the length and order of the offer_dirs')
    parser.add_argument('-model', required=False, type=str, default='qwen2.5:0.5b', help='Model to use for summarization')
    parser.add_argument('-m', required=False, type=str, default="update", help='Run mode: update (only run for new offers) or overwrite (run for all offers)')
    parser.add_argument('-verbosity', required=False, type=int, default=False, help='Verbose mode: 0 - silent, 1 - print system messages, 2 - print system messages and model outputs')
    return parser.parse_args()

def main():
    args = parse_args()
    for offer_dir, output_dir in zip(args.offer_dirs, args.output_dirs):
        for offer_path in offer_dir.glob('*.txt'):
            output_path = output_dir / offer_path.name.replace('.txt', '.json')
            offer_hash = calculate_file_hash(offer_path)
            if args.m == 'update' and output_path.exists():
                with open(output_path, 'r') as f:
                    summary = json.load(f)
                    if 'offer_hash' in summary and summary['offer_hash'] == offer_hash:
                        if (args.verbosity > 0):
                            print(f"Summary for {offer_path} already exists and is up to date")
                        continue

            handle_summarization(args.prompt_path, offer_path, output_path, args.model, verbosity=args.verbosity)
            if (args.verbosity > 0):
                print(f"Summary for {offer_path} created")

if __name__ == '__main__':
    main()