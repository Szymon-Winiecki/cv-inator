import argparse
import json
from pathlib import Path

from datetime import datetime

from cvinatordatamanager.DataServer import DataServer
from cvinatorprocessingtools.OffersSummarizer import OffersSummarizer
from cvinatorprocessingtools.SummariesEmbedder import SummariesEmbedder

def parse_args():
    parser = argparse.ArgumentParser(description='Prepare data  for CV-inator: load offers; summarize them and calc embeddings')
    parser.add_argument('-input', type=Path, required=True, help='Path to the JSON file with job offers')
    parser.add_argument('-data_dir', type=Path, required=True, help='Path to the cv-inator data directory')
    parser.add_argument('-summarization_model', type=str, default='llama3.2', help='Model to use for summarization (default: llama3.2)')
    parser.add_argument('-summarization_prompt', type=Path, default='prompts/summarization/prompt_jji.txt', help='Path to the prompt file for summarization (default: prompts/summarization/prompt_jji.txt)')
    parser.add_argument('-embedding_model', type=str, default='all-MiniLM-L12-v2', help='Model to use for embeddings (default: all-MiniLM-L12-v2)')
    parser.add_argument('-embedding_fields', type=str, nargs='+', default=['job_title', 'job_description', 'requirements'], help='Fields to embed in the summaries (default: job_title, job_description, requirements)')
    parser.add_argument('-top_n', type=int, default=None, help='Number of job offers to process (default: all)')
    parser.add_argument('-offset', type=int, default=0, help='Offset for job offers (default: 0)')
    parser.add_argument('-verbose', action='store_true', help='Enable verbose output')
    
    return parser.parse_args()

def main():
    args = parse_args()

    data_server = DataServer(args.data_dir)
    offer_summarizer = OffersSummarizer(data_server)
    summaries_embedder = SummariesEmbedder(data_server, args.embedding_model, args.embedding_fields)

    if not args.summarization_prompt.exists():
        raise FileNotFoundError(f"Prompt file {args.summarization_prompt} does not exist.")
    prompt = args.summarization_prompt.read_text(encoding='utf8')

    offers = json.loads(open(args.input, 'r', encoding='utf8').read())

    if args.top_n is not None:
        offers = offers[args.offset:args.offset + args.top_n]
    else:
        offers = offers[args.offset:]

    if args.verbose:
        print(f"Processing {len(offers)} offers from {args.input}")
        print(f"progress: 0/{len(offers)}")

    for i, offer in enumerate(offers):

        offer_frame = {
            'offer': offer,
            'source': 'unknown',
            'timestamp': int(datetime.now().timestamp())
        }

        offer_id = data_server.insert_offer(offer_frame)

        summary = offer_summarizer.summarize_offer(
            offer_id,
            prompt=prompt,
            model=args.summarization_model,
            LLM_engine='ollama'
        )

        summary_id = data_server.insert_summary(summary)

        embeddings, embeddings_info = summaries_embedder.embed_summary(summary_id)

        embeddings_id = data_server.insert_embedding(embeddings, embeddings_info)

        if args.verbose:
            print(f"Progress: {i + 1}/{len(offers)}")

    
    if args.verbose:
        print(f"Data preparation completed. {len(offers)} offers processed.")
        print(f"Summaries and embeddings saved to server at {args.data_dir}")


if __name__ == '__main__':
    main()