import json
from datetime import datetime

from cvinatordatamanager.DataServer import DataServer

from .utils.llm_helpers import execute_prompt
from .utils.helpers import get_current_timestamp

class OffersSummarizer:
    def __init__(self, data_server: DataServer, offer_placeholder='${OFFER}') -> None:

        # placeholder to be replaced with the offer in the prompt
        self.offer_placeholder = offer_placeholder

        self.data_server = data_server

    def summarize_offer(self, offer_id: int, prompt: str, model: str, LLM_engine: str) -> dict:
        
        offer = self.data_server.get_offer_by_id(offer_id)['offer']

        filled_prompt = prompt.replace(self.offer_placeholder, json.dumps(offer))

        llm_output = execute_prompt(filled_prompt, model, LLM_engine)

        # LLM outputs JSON as a string, so we need to parse it
        summary = json.loads(llm_output["response"])

        result = {
            'offer_summary': summary,
            'info': llm_output['info'],
            'model': model,
            'prompt': prompt,
            'offer_id': offer_id,
            'timestamp' : get_current_timestamp(),
            'LLM_engine': LLM_engine,
        }

        return result