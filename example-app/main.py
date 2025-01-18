import json
from datetime import datetime

from cvinatordatamanager.DataServer import DataServer
from cvinatorprocessingtools.OffersSummarizer import OffersSummarizer

def main():
    data_server = DataServer('example-app/data', create_if_not_exists=True, recreate_if_outdated=True)
    offers_summarizer = OffersSummarizer(data_server)
    
    offer_path = 'offers/json/00.json'
    with open(offer_path, "r", encoding="utf8") as file:
        offer = json.load(file)

    data_server.insert_offer(offer)

    random_offer_id = data_server.get_offers_ids()[0]

    prompt_path = "prompts/summarization/prompt.txt"

    with open(prompt_path, "r") as file:
        prompt = file.read()

    summary = offers_summarizer.summarize_offer(random_offer_id, prompt, 'llama3.2', 'ollama')

    data_server.insert_summary(summary)

    print(data_server.get_newest_summary_by_offer_id(random_offer_id))

    data_server.close()

main()