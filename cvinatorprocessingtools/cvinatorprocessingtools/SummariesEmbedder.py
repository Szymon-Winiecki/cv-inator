import numpy as np
from sentence_transformers import SentenceTransformer

from cvinatordatamanager.DataServer import DataServer

from .utils.helpers import get_current_timestamp

class SummariesEmbedder:
    def __init__(self, data_server: DataServer, model_name : str, fields_to_embed : list) -> None:
        self.data_server = data_server
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_size = self.model.get_sentence_embedding_dimension()
        self.fields_to_embed = fields_to_embed

    def calc_embedding(self, summary : dict) -> np.ndarray:  

        embeddings = np.zeros((len(self.fields_to_embed), self.embedding_size))

        for field_ind, field in enumerate(self.fields_to_embed):
            if not field in summary:
                summary[field] = 'N/A'
            text = ", ".join(summary[field]) if type(summary[field]) == list else summary[field]
            embeddings[field_ind] = self.model.encode(text)

        return embeddings

    def embed_summary(self, summary_id : int) -> tuple:
       
        summary = self.data_server.get_summary_by_id(summary_id)['offer_summary']

        embeddings = self.calc_embedding(summary)

        embeddings_info = {
            'embedded_fields': self.fields_to_embed,
            'summary_id': summary_id,
            'model': self.model_name,
            'timestamp': get_current_timestamp()
        }

        return embeddings, embeddings_info