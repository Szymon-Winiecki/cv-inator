from datetime import datetime

class PromptsController:
    @staticmethod
    def get_prompts(conn):
        cur = conn.cursor()
        cur.execute('''SELECT * FROM prompts''')
        return cur.fetchall()
    
    @staticmethod
    def get_prompt_by_id(conn, prompt_id):
        cur = conn.cursor()
        cur.execute('''SELECT * FROM prompts WHERE id=?''', (prompt_id,))
        return cur.fetchone()
    
    @staticmethod
    def insert_or_get_id(conn, prompt):
        cur = conn.cursor()
        cur.execute('''SELECT id FROM prompts WHERE prompt=?''', (prompt,))
        prompt_id = cur.fetchone()
        if prompt_id is None:
            cur.execute('''INSERT INTO prompts (prompt, added_at) VALUES (?, ?)''', (prompt, int(datetime.now().timestamp())))
            conn.commit()
            return cur.lastrowid
        return prompt_id[0]