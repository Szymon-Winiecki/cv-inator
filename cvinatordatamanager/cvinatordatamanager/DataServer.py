import sqlite3
from pathlib import Path
from datetime import datetime

from .utils.queries import DatabaseManagementQueries

from .controllers.OffersController import OffersController
from .controllers.SummariesController import SummariesController
from .controllers.EmbeddingsController import EmbeddingsController

class DataServer:
    DATABASE_SCHEME_VERSION = 9
    DATABASE_FILE = Path('data.db')

    def __init__(self, data_dir, create_if_not_exists=True, recreate_if_outdated=False):
        if not type(data_dir) == Path:
            data_dir = Path(data_dir)

        self.data_dir = data_dir

        if not (data_dir / DataServer.DATABASE_FILE).exists():
            if not create_if_not_exists:
                raise FileNotFoundError('Database file not found')
            self.__create_database(data_dir)

        self.conn = sqlite3.connect(data_dir / DataServer.DATABASE_FILE)

        if int(self.__get_info("DATABASE_SCHEME_VERSION")) != DataServer.DATABASE_SCHEME_VERSION:
            if recreate_if_outdated:
                self.reset_database()
            else:
                raise Exception("Database scheme version mismatch, set recreate_if_outdated=True to recreate the database (all data will be lost)")
            
        

    def __create_database(self, data_dir : Path):

        data_dir.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(data_dir / DataServer.DATABASE_FILE)
        cur = conn.cursor()

        cur.execute(DatabaseManagementQueries.create_table_info)
        cur.execute(DatabaseManagementQueries.create_table_offers)
        cur.execute(DatabaseManagementQueries.create_table_summaries)
        cur.execute(DatabaseManagementQueries.create_table_embeddings)
        cur.execute(DatabaseManagementQueries.create_table_prompts)

        cur.execute(DatabaseManagementQueries.insert_info, ("DATABASE_SCHEME_VERSION", DataServer.DATABASE_SCHEME_VERSION))
        cur.execute(DatabaseManagementQueries.insert_info, ("CREATED_AT", datetime.now().isoformat(' ')))

        conn.commit()
        conn.close()

    def __delete_database(self, data_dir : Path):

        EmbeddingsController.erease_embeddings_files(data_dir)
        SummariesController.erease_summaries_files(data_dir)
        OffersController.erease_offers_files(data_dir)

        if (data_dir / DataServer.DATABASE_FILE).exists():
            (data_dir / DataServer.DATABASE_FILE).unlink()
        

    def reset_database(self):
        self.conn.close()
        self.__delete_database(self.data_dir)
        self.__create_database(self.data_dir)
        self.conn = sqlite3.connect(self.data_dir / DataServer.DATABASE_FILE)


    def __get_info(self, key):
        cur = self.conn.cursor()
        cur.execute(DatabaseManagementQueries.get_info, (key,))
        return cur.fetchone()[0]

    def __del__(self):
        self.close()

    def close(self):
        self.conn.close()

    ###
    # Offers
    ###

    def get_offers_ids(self):
        return OffersController.get_offers_ids(self.conn)
    
    def get_offers(self):
        return OffersController.get_offers(self.conn, self.data_dir)

    def get_offer_by_id(self, offer_id):
        return OffersController.get_offer_by_id(self.conn, self.data_dir, offer_id)
    
    def get_offers_by_ids(self, offers_ids):
        return OffersController.get_offers_by_ids(self.conn, self.data_dir, offers_ids)
    
    def get_offer_by_embedding_id(self, embedding_id):
        return OffersController.get_offer_by_embeding_id(self.conn, self.data_dir, embedding_id)
    
    def get_offers_ids_by_embeddings_ids(self, embeddings_ids):
        return OffersController.get_offers_ids_by_embeddings_ids(self.conn, embeddings_ids)
    
    ###
    # Insert offer
    #
    # offer: dict of strcture:
    # {
    # "offer": { ... },
    # "source": <source : string>,
    # "timestamp": <timestamp : int>,
    # }
    def insert_offer(self, offer):
        return OffersController.insert_offer(self.conn, self.data_dir, offer)
    
    def delete_offer(self, offer_id):
        return OffersController.delete_offer(self.conn, self.data_dir, offer_id)
    

    ###
    # Summaries
    ###

    def get_summaries(self):
        return SummariesController.get_summaries(self.conn, self.data_dir)

    def get_summaries_ids(self):
        return SummariesController.get_summaries_ids(self.conn)
    
    def get_summary_by_id(self, summary_id):
        return SummariesController.get_summary_by_id(self.conn, self.data_dir, summary_id)
    
    def get_summaries_by_offer_id(self, offer_id):
        return SummariesController.get_summaries_by_offer_id(self.conn, self.data_dir, offer_id)
    
    def get_newest_summary_by_offer_id(self, offer_id):
        return SummariesController.get_newest_summary_by_offer_id(self.conn, self.data_dir, offer_id)
    
    def get_summary_by_embedding_id(self, embedding_id):
        return SummariesController.get_summary_by_embedding_id(self.conn, self.data_dir, embedding_id)
    

    ###
    # Insert summary
    #
    # summary: dict of strcture:
    # {
    #     "offer_summary": { ... },
    #     "info": { ... },
    #     "model": <model_name : string>,
    #     "prompt": <prompt_template : string>,
    #     "offer_id": <offer_id : int>,
    #     "timestamp": <timestamp : int>,
    #     "LLM_engine": <LLM_engnine_name : string>
    # }
    def insert_summary(self, summary):
        return SummariesController.insert_summary(self.conn, self.data_dir, summary)
    
    def delete_summary(self, summary_id):
        return SummariesController.delete_summary(self.conn, self.data_dir, summary_id)
    

    ###
    # Embeddings
    ###

    def get_embeddings_ids(self):
        return EmbeddingsController.get_embeddings_ids(self.conn)
    
    def get_embedding_by_id(self, embedding_id):
        return EmbeddingsController.get_embedding_by_id(self.conn, self.data_dir, embedding_id)
    
    def get_embeddings_ids_by_summary_id(self, summary_id):
        return EmbeddingsController.get_embeddings_ids_by_summary_id(self.conn, summary_id)
    
    def get_newest_embedding_id_by_summary_id(self, summary_id):
        return EmbeddingsController.get_newest_embedding_id_by_summary_id(self.conn, summary_id)
    
    def get_embeddings_ids_by_offer_id(self, offer_id):
        return EmbeddingsController.get_embeddings_ids_by_offer_id(self.conn, offer_id)
    
    def get_newest_embedding_id_by_offer_id(self, offer_id):
        return EmbeddingsController.get_newest_embedding_id_by_offer_id(self.conn, offer_id)
    
    ###
    # Insert Embedding
    #
    # embedding : numpy array
    # embedding_info: dict of structure:
    # {
    #     "embedded_fields": [
    #         <field_1>, <field_2>, ...
    #     ],
    #     "summary_id": <summary_id : int>,
    #     "model": <model_name : string>,
    #     "timestamp": <timestamp : int>,
    # }
    ###
    def insert_embedding(self, embedding, embedding_info):
        return EmbeddingsController.insert_embedding(self.conn, self.data_dir, embedding, embedding_info)
    
    def delete_embedding(self, embedding_id):
        return EmbeddingsController.delete_embedding(self.conn, self.data_dir, embedding_id)
    
    def delete_all_embeddings(self):
        return EmbeddingsController.delete_all_embeddings(self.conn, self.data_dir)
    

    ###
    # Offer features - embeddings, lists etc from summaries for comparison
    ###

    # features: dict of structure:
    # {
    #     <feature_1>: <"embedding" | "raw">,
    #     <feature_2>: <"embedding" | "raw">,
    #     ...
    # }
    def get_offer_features(self, embedding_id, features):
        return EmbeddingsController.get_features_by_embedding_id(self.conn, self.data_dir, embedding_id, features)
