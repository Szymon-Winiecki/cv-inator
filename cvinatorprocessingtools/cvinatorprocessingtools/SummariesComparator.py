import numpy as np

from sentence_transformers import SentenceTransformer

from cvinatordatamanager.DataServer import DataServer

class SummariesComparator:

    # comparation_sheme : dict of structure:
    # {
    #     "field_1": {
    #         "weight": <weight : float>,
    #         "method": <"embedding" | "list">
    #     },
    #     "field_2": { ... },
    #     ...
    # },
    def __init__(self, data_server : DataServer, comparation_sheme : dict):
        self.data_server = data_server
        self.comparation_sheme = comparation_sheme
    
    #  returns dict of structure:
    # {
    #     <1st_most_simmilar_embedding_id> : <similarity>,
    #     <2nd_most_simmilar_embedding_id> : <similarity>,
    #     ...
    # }
    def get_most_similar_summaries(self, target_embedding_id : int, embeddings_ids : list, top_n : int | None = None, similarity_threshold : float | None  = None) -> dict:
        features_query =  self.__get_features_query()

        target_features = self.data_server.get_offer_features(target_embedding_id, features_query)
        other_features = [ self.data_server.get_offer_features(embedding_id, features_query) for embedding_id in embeddings_ids ]

        similarities, _ = self.__calc_similarity([target_features], other_features)

        most_similar_ord = np.argsort(similarities, axis=1)

        if top_n != None and top_n >= 0:
            most_similar_ord = most_similar_ord[:, -top_n:]

        if similarity_threshold != None and similarity_threshold >= 0:
            most_similar_ord = most_similar_ord[similarities[most_similar_ord] >= similarity_threshold]

        most_similar_ord = np.flip(most_similar_ord, axis=1)

        return { embeddings_ids[i] : similarities[0, i] for i in most_similar_ord[0] }



    def get_similarities(self, embeddings_ids : list) -> dict:
        features_query =  self.__get_features_query()
            
        features = [ self.data_server.get_offer_features(embedding_id, features_query) for embedding_id in embeddings_ids ]

        similarities, partial_similarities = self.__calc_similarity(features, features)

        return similarities, partial_similarities
    
    def __get_features_query(self) -> dict:
        features_query = {}
        for field in self.comparation_sheme:
            if self.comparation_sheme[field]["method"] == "embedding":
                features_query[field] = "embedding"
            elif self.comparation_sheme[field]["method"] == "list":
                features_query[field] = "raw"
            else:
                raise ValueError("Unknown method of comparison")
        
        return features_query

    def __compare_lists(self, to_lists : list, of_lists : list) -> np.ndarray:

        similarities = np.zeros((len(to_lists), len(of_lists)))

        to_lists = [ set([l.lower() for l in list]) for list in to_lists ]
        of_lists = [ set([l.lower() for l in list]) for list in of_lists ]

        for a, to in enumerate(to_lists):
            for b, of in enumerate(of_lists):
                common = len(to & of)
                similarities[a, b] = common / len(of) if len(of) > 0 else 1

        return similarities

    def __calc_similarity(self, to_offers_features : dict, of_offers_features : dict) -> np.ndarray:

        if len(to_offers_features) == 0 or len(of_offers_features) == 0:
            return np.zeros((0, 0))
        
        num_fields = len(self.comparation_sheme)
        num_to = len(to_offers_features)
        num_of = len(of_offers_features)

        partial_similarities = np.zeros((num_fields, num_to, num_of))
        similarities = np.zeros((num_to, num_of))

        model = SentenceTransformer(to_offers_features[0]["embedding_model"])
        embeddings_size = model.get_sentence_embedding_dimension()

        for field_ind, field in enumerate(self.comparation_sheme):
            if self.comparation_sheme[field]["method"] == "embedding":
                to_merged_field = np.zeros((len(to_offers_features), embeddings_size))
                for i, offer_features in enumerate(to_offers_features):
                    to_merged_field[i] = offer_features[field]

                of_merged_field = np.zeros((len(of_offers_features), embeddings_size))
                for i, offer_features in enumerate(of_offers_features):
                    of_merged_field[i] = offer_features[field]

                partial_similarities[field_ind] = model.similarity(to_merged_field, of_merged_field)

            elif self.comparation_sheme[field]["method"] == "list":
                to_merged_field = [ offer_features[field] for offer_features in to_offers_features ]

                of_merged_field = [ offer_features[field] for offer_features in of_offers_features ]

                partial_similarities[field_ind] = self.__compare_lists(to_merged_field, of_merged_field)

            else:
                raise ValueError("Unknown method of comparison")
            
            similarities += self.comparation_sheme[field]["weight"] * partial_similarities[field_ind]

        similarities /= sum([ self.comparation_sheme[field]["weight"] for field in self.comparation_sheme ])

        return similarities, partial_similarities