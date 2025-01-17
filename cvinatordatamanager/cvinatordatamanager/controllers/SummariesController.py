from  ..utils.fs import calculate_file_hash, save_json, load_json
from pathlib import Path

from .EmbeddingsController import EmbeddingsController
from .PromptsController import PromptsController

class SummariesController:
    SUMMARIES_DIR = Path('summaries')

    @staticmethod
    def get_summaries(conn, data_dir):
        cur = conn.cursor()
        cur.execute('''SELECT id, path FROM summaries''')
        
        summaries = {}
        for id, relative_path in cur.fetchall():
            summaries[id] = load_json(data_dir / relative_path)
        
        return summaries
    
    @staticmethod
    def get_summaries_ids(conn):
        cur = conn.cursor()
        cur.execute('''SELECT id FROM summaries''')
        return [t[0] for t in cur.fetchall()]
    
    @staticmethod
    def get_summary_by_id(conn, data_dir, summary_id):
        cur = conn.cursor()
        cur.execute('''SELECT path FROM summaries WHERE id=?''', (summary_id,))
        row = cur.fetchone()

        if row is None:
            return None
        
        relative_path = row[0]
        summary = load_json(data_dir / relative_path)

        return summary

    
    @staticmethod
    def get_summaries_by_offer_id(conn, data_dir, offer_id):
        cur = conn.cursor()
        cur.execute('''SELECT id, path FROM summaries WHERE offer_id=?''', (offer_id,))

        summaries = {}

        for id, relative_path in cur.fetchall():
            summaries[id] = load_json(data_dir / relative_path)

        return summaries

    
    @staticmethod
    def get_newest_summary_by_offer_id(conn, data_dir, offer_id):
        cur = conn.cursor()
        cur.execute('''SELECT path FROM summaries WHERE offer_id=? ORDER BY generated_at DESC LIMIT 1''', (offer_id,))
        row = cur.fetchone()

        if row is None:
            return None
        
        relative_path = row[0]
        summary = load_json(data_dir / relative_path)

        return summary
    
    @staticmethod
    def insert_summary(conn, data_dir, summary):

        prompt_id = PromptsController.insert_or_get_id(conn, summary['prompt'])

        del summary['prompt']
        summary['prompt_id'] = prompt_id

        summary_tuple = (summary['offer_id'], summary['model'], summary['LLM_engine'], prompt_id, summary['timestamp'])
        
        cur = conn.cursor()
        cur.execute('''INSERT INTO summaries (offer_id, model, llm_engine, prompt_id, generated_at) VALUES (?, ?, ?, ?, ?)''', summary_tuple)
        
        relative_path = SummariesController.SUMMARIES_DIR / f"{cur.lastrowid}.json"
        full_path = data_dir / relative_path
        save_json(full_path, summary)
        
        update_tuple = (str(relative_path), calculate_file_hash(full_path), cur.lastrowid)
        cur.execute('''UPDATE summaries SET path=?, hash=? WHERE id=?''', update_tuple)
        conn.commit()
        
        return cur.lastrowid
    
    @staticmethod
    def delete_summary(conn, data_dir, summary_id):
        cur = conn.cursor()
        cur.execute('''SELECT path FROM summaries WHERE id=?''', (summary_id,))
        summary_path = cur.fetchone()[0]
        
        cur.execute('''DELETE FROM summaries WHERE id=?''', (summary_id,))
        conn.commit()

        full_path = data_dir / summary_path
        if full_path.exists():
            full_path.unlink()

        EmbeddingsController.delete_embeddings_by_summary_id(conn, data_dir, summary_id)
        

    @staticmethod
    def delete_summaries_by_offer_id(conn, data_dir, offer_id):
        cur = conn.cursor()
        cur.execute('''SELECT id FROM summaries WHERE offer_id=?''', (offer_id,))
        summary_ids = cur.fetchall()

        for summary_id in summary_ids:
            SummariesController.delete_summary(conn, data_dir, summary_id[0])

    @staticmethod
    def erease_summaries_files(data_dir):
        summaries_dir = data_dir / SummariesController.SUMMARIES_DIR
        if summaries_dir.exists():
            for summary_file in summaries_dir.iterdir():
                if summary_file.is_file() and summary_file.suffix == '.json':
                    summary_file.unlink()
            summaries_dir.rmdir()