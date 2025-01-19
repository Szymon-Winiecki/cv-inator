import json
from datetime import datetime
from pathlib import Path


from cvinatordatamanager.DataServer import DataServer
from cvinatorprocessingtools.OffersSummarizer import OffersSummarizer
from  cvinatorprocessingtools.SummariesEmbedder import SummariesEmbedder
from  cvinatorprocessingtools.SummariesComparator import SummariesComparator
from  cvinatorprocessingtools.SimilarityVisualizer import SimilarityVisualizer

def insert_jji_offers(data_server, json_path, top_n=10):
    with open(json_path, "r", encoding="utf8") as file:
        offers = json.load(file)

    for offer in offers[:top_n]:
        processed_offer = {
            'offer': offer,
            'source': 'https://justjoin.it/',
            'timestamp': int(datetime.now().timestamp()),
        }
        data_server.insert_offer(processed_offer)

def main():
    data_server = DataServer('example-app/data', create_if_not_exists=True, recreate_if_outdated=True)

    data_server.reset_database()
    
    insert_jji_offers(data_server, 'job_offers.json', top_n=100)

    offers_ids = data_server.get_offers_ids()

    prompt_path = "prompts/summarization/prompt_jji.txt"
    with open(prompt_path, "r") as file:
        prompt = file.read()

    offers_summarizer = OffersSummarizer(data_server)

    for id in offers_ids:
        summary = offers_summarizer.summarize_offer(id, prompt, 'llama3.2', 'ollama')
        data_server.insert_summary(summary)

    fields_to_embed = ['job_title', 'job_description', 'requirements']
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
        'required_skills': {
            'method': 'list',
            'weight': 2.0
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