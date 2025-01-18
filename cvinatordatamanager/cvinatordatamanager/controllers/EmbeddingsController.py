from  ..utils.fs import calculate_file_hash, save_json
from pathlib import Path
import numpy as np

class EmbeddingsController:
    EmbeddingsDir = Path('embeddings')

    @staticmethod
    def get_embeddings(conn):
        cur = conn.cursor()
        cur.execute('''SELECT * FROM embeddings''')
        return cur.fetchall()
    
    @staticmethod
    def get_embedding_by_id(conn, embedding_id):
        cur = conn.cursor()
        cur.execute('''SELECT * FROM embeddings WHERE id=?''', (embedding_id,))
        return cur.fetchone()
    
    @staticmethod
    def get_embeddings_by_summary_id(conn, summary_id):
        cur = conn.cursor()
        cur.execute('''SELECT * FROM embeddings WHERE summary_id=?''', (summary_id,))
        return cur.fetchall()
    
    @staticmethod
    def get_newest_embedding_by_summary_id(conn, summary_id):
        cur = conn.cursor()
        cur.execute('''SELECT * FROM embeddings WHERE summary_id=? ORDER BY generated_at DESC LIMIT 1''', (summary_id,))
        return cur.fetchone()

    @staticmethod
    def get_embeddings_by_offer_id(conn, offer_id):
        cur = conn.cursor()
        cur.execute('''SELECT embeddings.* FROM embeddings JOIN summaries ON embeddings.summary_id = summaries.id WHERE summaries.offer_id=?''', (offer_id,))
        return cur.fetchall()
    
    @staticmethod
    def get_newest_embedding_by_offer_id(conn, offer_id):
        cur = conn.cursor()
        cur.execute('''SELECT embeddings.* FROM embeddings JOIN summaries ON embeddings.summary_id = summaries.id WHERE summaries.offer_id=? ORDER BY embeddings.generated_at DESC LIMIT 1''', (offer_id,))
        return cur.fetchone()
    
    @staticmethod
    def insert_embedding(conn, data_dir, embedding, embedding_info):
        embedding_tuple = (embedding['summary_id'], embedding['model'], embedding['timestamp'])
        
        cur = conn.cursor()
        cur.execute('''INSERT INTO embeddings (summary_id, model, generated_at) VALUES (?, ?, ?)''', embedding_tuple)
        
        relative_embedding_path = EmbeddingsController.EmbeddingsDir / f"{cur.lastrowid}.npy"
        relative_info_path = EmbeddingsController.EmbeddingsDir / f"{cur.lastrowid}_info.json"
        full_embedding_path = data_dir / relative_embedding_path
        full_info_path = data_dir / relative_info_path

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
