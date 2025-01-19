from  ..utils.fs import calculate_file_hash, save_json, load_json
from pathlib import Path

class OffersController:
    OFFERS_DIR = Path('offers')

    @staticmethod
    def get_offers_ids(conn):
        cur = conn.cursor()
        cur.execute('''SELECT id FROM offers''')
        return [t[0] for t in cur.fetchall()]
    
    @staticmethod
    def get_offers(conn, data_dir):
        cur = conn.cursor()
        cur.execute('''SELECT id, path FROM offers''')

        offers = {}

        for id, relative_path in cur.fetchall():
            offers[id] = load_json(data_dir / relative_path)

        return offers
    
    @staticmethod
    def get_offer_by_id(conn, data_dir, offer_id):
        cur = conn.cursor()
        cur.execute('''SELECT path FROM offers WHERE id=?''', (offer_id,))
        row = cur.fetchone()
        
        if row is None:
            return None

        relativepath = row[0]
        offer = load_json(data_dir / relativepath)

        return offer
    
    @staticmethod
    def get_offer_by_embeding_id(conn, data_dir, embedding_id):
        cur = conn.cursor()
        cur.execute('''SELECT summaries.offer_id FROM embeddings JOIN summaries ON embeddings.summary_id = summaries.id WHERE embeddings.id=?''', (embedding_id,))
        row = cur.fetchone()

        if row is None:
            return None
        
        offer_id = row[0]
        return OffersController.get_offer_by_id(conn, data_dir, offer_id)
    
    @staticmethod
    def insert_offer(conn, data_dir, offer):

        offer_tuple = (offer['source'], offer['timestamp'])

        cur = conn.cursor()
        cur.execute('''INSERT INTO offers (source, scrapped_at) VALUES (?, ?)''', offer_tuple)

        relative_path = OffersController.OFFERS_DIR / f"{cur.lastrowid}.json"
        full_path = data_dir / relative_path
        save_json(full_path, offer)

        update_tuple = (str(relative_path), calculate_file_hash(full_path), cur.lastrowid)
        cur.execute('''UPDATE offers SET path=?, hash=? WHERE id=?''', update_tuple)
        conn.commit()

        return cur.lastrowid
    
    @staticmethod
    def delete_offer(conn, data_dir, offer_id):
        cur = conn.cursor()
        cur.execute('''SELECT path FROM offers WHERE id=?''', (offer_id,))
        offer_path = cur.fetchone()[0]

        cur.execute('''DELETE FROM offers WHERE id=?''', (offer_id,))
        conn.commit()

        full_path = data_dir / offer_path
        if full_path.exists():
            full_path.unlink()

        from .SummariesController import SummariesController
        SummariesController.delete_summaries_by_offer_id(conn, data_dir, offer_id)
    

    ###
    # remove all json files from offers directory
    # and remove the directory itself if it is empty (no other files)
    ###
    @staticmethod
    def erease_offers_files(data_dir):
        offers_dir = data_dir / OffersController.OFFERS_DIR
        if offers_dir.exists():
            for file in offers_dir.iterdir():
                if file.is_file() and file.suffix == '.json':
                    file.unlink()
            offers_dir.rmdir()