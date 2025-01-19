import json
from datetime import datetime
from pathlib import Path


from cvinatordatamanager.DataServer import DataServer
from cvinatorprocessingtools.OffersSummarizer import OffersSummarizer
from  cvinatorprocessingtools.SummariesEmbedder import SummariesEmbedder
from  cvinatorprocessingtools.SummariesComparator import SummariesComparator
from  cvinatorprocessingtools.SimilarityVisualizer import SimilarityVisualizer

def main():
    data_server = DataServer('example-app/data', create_if_not_exists=True, recreate_if_outdated=True)
    
    offer_paths = ['offers/json/00.json', 'offers/json/01.json', 'offers/json/03.json', 'offers/json/04.json', 'offers/json/05.json']

    for offer_path in offer_paths:
        with open(offer_path, "r", encoding="utf8") as file:
            offer = json.load(file)

        data_server.insert_offer(offer)

    offers_ids = data_server.get_offers_ids()

    prompt_path = "prompts/summarization/prompt.txt"

    with open(prompt_path, "r") as file:
        prompt = file.read()

    offers_summarizer = OffersSummarizer(data_server)

    for id in offers_ids:
        summary = offers_summarizer.summarize_offer(id, prompt, 'llama3.2', 'ollama')
        data_server.insert_summary(summary)

    fields_to_embed = ['job_title', 'job_description', 'requirements', 'benefits']
    summaries_embedder = SummariesEmbedder(data_server, 'paraphrase-albert-small-v2', fields_to_embed)
    summaries_ids = data_server.get_summaries_ids()

    for id in summaries_ids:
        embeddings, embeddings_info = summaries_embedder.embed_summary(id)
        data_server.insert_embedding(embeddings, embeddings_info)

    comparation_scheme = {
        'job_title': {
            'method': 'embedding',
            'weight': 1.0
        },
        'job_description': {
            'method': 'embedding',
            'weight': 2.0
        },
        'requirements': {
            'method': 'embedding',
            'weight': 1.0
        },
        'benefits': {
            'method': 'embedding',
            'weight': 0.5
        },
        'required_skills': {
            'method': 'list',
            'weight': 2.0
        },
        'nice_to_have_skills': {
            'method': 'list',
            'weight': 1.0
        }
    }
    
    summaries_comparator = SummariesComparator(data_server, comparation_scheme)
    embeddings_ids = data_server.get_embeddings_ids()

    similarities, partial_similarities = summaries_comparator.get_similarities(embeddings_ids)

    most_similar = summaries_comparator.get_most_similar_summaries(embeddings_ids[0], embeddings_ids)

    SimilarityVisualizer.plot_similarity(similarities, embeddings_ids, embeddings_ids, Path('example-app/output/final_similarity_matrix.png'))

    print(most_similar)

    data_server.close()

main()