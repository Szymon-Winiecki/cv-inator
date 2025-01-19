from  ..utils.fs import calculate_file_hash, save_json, load_json
from pathlib import Path
import numpy as np

from .SummariesController import SummariesController

class EmbeddingsController:
    EmbeddingsDir = Path('embeddings')

    @staticmethod
    def get_embeddings_ids(conn):
        cur = conn.cursor()
        cur.execute('''SELECT id FROM embeddings''')
        return [t[0] for t in cur.fetchall()]
    
    @staticmethod
    def get_embedding_by_id(conn, data_dir, embedding_id):
        cur = conn.cursor()
        cur.execute('''SELECT embedding_path, info_path FROM embeddings WHERE id=?''', (embedding_id,))
        row = cur.fetchone()

        if row is None:
            return None
        
        embedding_path = data_dir / row[0]
        info_path = data_dir / row[1]

        embedding = np.load(embedding_path)
        embedding_info = load_json(info_path)

        return embedding, embedding_info
    
    @staticmethod
    def get_embeddings_ids_by_summary_id(conn, summary_id):
        cur = conn.cursor()
        cur.execute('''SELECT id FROM embeddings WHERE summary_id=?''', (summary_id,))
        return [t[0] for t in cur.fetchall()]
    
    @staticmethod
    def get_newest_embedding_id_by_summary_id(conn, summary_id):
        cur = conn.cursor()
        cur.execute('''SELECT id FROM embeddings WHERE summary_id=? ORDER BY generated_at DESC LIMIT 1''', (summary_id,))
        row = cur.fetchone()
        return row[0] if row is not None else None

    @staticmethod
    def get_embeddings_ids_by_offer_id(conn, offer_id):
        cur = conn.cursor()
        cur.execute('''SELECT embeddings.id FROM embeddings JOIN summaries ON embeddings.summary_id = summaries.id WHERE summaries.offer_id=?''', (offer_id,))
        return [t[0] for t in cur.fetchall()]
    
    @staticmethod
    def get_newest_embedding_id_by_offer_id(conn, offer_id):
        cur = conn.cursor()
        cur.execute('''SELECT embeddings.id FROM embeddings JOIN summaries ON embeddings.summary_id = summaries.id WHERE summaries.offer_id=? ORDER BY embeddings.generated_at DESC LIMIT 1''', (offer_id,))
        row = cur.fetchone()
        return row[0] if row is not None else None
    

    # features: dict of structure:
    # {
    #     <feature_1>: <"embedding" | "raw">,
    #     <feature_2>: <"embedding" | "raw">,
    #     ...
    # }
    @staticmethod
    def get_features_by_embedding_id(conn, data_dir, embedding_id, features):
        cur = conn.cursor()
        cur.execute('''SELECT embedding_path, info_path, summary_id FROM embeddings WHERE id=?''', (embedding_id,))
        row = cur.fetchone()
        
        if row is None:
            return None
        
        embedding_path = data_dir / row[0]
        info_path = data_dir / row[1]
        summary_id = row[2]

        embedding = np.load(embedding_path)
        embedding_info = load_json(info_path)
        summary = SummariesController.get_summary_by_id(conn, data_dir, summary_id)["offer_summary"]

        features_dict = {
            'embedding_model': embedding_info['model'],
        }

        for feature in features:
            if features[feature] == 'embedding' and feature in embedding_info['embedded_fields']:
                features_dict[feature] = embedding[embedding_info['embedded_fields'].index(feature)]
            elif features[feature] == 'raw' and feature in summary:
                features_dict[feature] = summary[feature]
            else:
                return None
        
        return features_dict
        
    
    @staticmethod
    def insert_embedding(conn, data_dir, embedding, embedding_info):
        embedding_tuple = (embedding_info['summary_id'], embedding_info['model'], embedding_info['timestamp'])
        
        cur = conn.cursor()
        cur.execute('''INSERT INTO embeddings (summary_id, model, generated_at) VALUES (?, ?, ?)''', embedding_tuple)
        
        relative_embedding_path = EmbeddingsController.EmbeddingsDir / f"{cur.lastrowid}.npy"
        relative_info_path = EmbeddingsController.EmbeddingsDir / f"{cur.lastrowid}_info.json"
        full_embedding_path = data_dir / relative_embedding_path
        full_info_path = data_dir / relative_info_path

        full_embedding_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(full_embedding_path, embedding)
        save_json(full_info_path, embedding_info)
        
        update_tuple = (str(relative_embedding_path), str(relative_info_path), calculate_file_hash(full_embedding_path), calculate_file_hash(full_info_path), cur.lastrowid)
        cur.execute('''UPDATE embeddings SET embedding_path=?, info_path=?, embedding_hash=?, info_hash=? WHERE id=?''', update_tuple)
        conn.commit()
        
        return cur.lastrowid
    
    @staticmethod
    def delete_embedding(conn, data_dir, embedding_id):
        cur = conn.cursor()
        cur.execute('''SELECT embedding_path, info_path FROM embeddings WHERE id=?''', (embedding_id,))
        embedding_path, info_path = cur.fetchone()
        
        cur.execute('''DELETE FROM embeddings WHERE id=?''', (embedding_id,))
        conn.commit()

        full_embedding_path = data_dir / embedding_path
        full_info_path = data_dir / info_path
        if full_embedding_path.exists():
            full_embedding_path.unlink()
        if full_info_path.exists():
            full_info_path.unlink()

    @staticmethod
    def delete_embeddings_by_summary_id(conn, data_dir, summary_id):
        cur = conn.cursor()
        cur.execute('''SELECT id FROM embeddings WHERE summary_id=?''', (summary_id,))

        for embedding_id in cur.fetchall():
            EmbeddingsController.delete_embedding(conn, data_dir, embedding_id[0])

    @staticmethod
    def erease_embeddings_files(data_dir):
        embeddings_dir = data_dir / EmbeddingsController.EmbeddingsDir
        if embeddings_dir.exists():
            for file in embeddings_dir.iterdir():
                if file.is_file() and (file.suffix == '.npy' or file.suffix == '.json'):
                    file.unlink()
            embeddings_dir.rmdir()
