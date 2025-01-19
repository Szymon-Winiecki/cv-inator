class DatabaseManagementQueries:
    create_table_info = '''CREATE TABLE info (
        id integer PRIMARY KEY,
        key text,
        value text
    );'''

    insert_info = '''INSERT INTO info (key, value) VALUES (?, ?);'''

    get_info = '''SELECT value FROM info WHERE key=?;'''

    update_info = '''UPDATE info SET value=? WHERE key=?;'''

    create_table_offers = '''CREATE TABLE offers (
        id integer PRIMARY KEY,
        path text,
        source text,
        hash text,
        scrapped_at integer
    );'''

    create_table_summaries = '''CREATE TABLE summaries (
        id integer PRIMARY KEY,
        offer_id integer,
        path text,
        hash text,
        model text,
        llm_engine text,
        prompt_id integer,
        generated_at integer,
        FOREIGN KEY (offer_id) REFERENCES offers(id)
        FOREIGN KEY (prompt_id) REFERENCES prompts(id)
    );'''

    create_table_embeddings = '''CREATE TABLE embeddings (
        id integer PRIMARY KEY,
        summary_id integer,
        embedding_path text,
        info_path text,
        embedding_hash text,
        info_hash text,
        model text,
        generated_at integer,
        FOREIGN KEY (summary_id) REFERENCES summaries(id)
    );'''

    create_table_prompts = '''CREATE TABLE prompts (
        id integer PRIMARY KEY,
        prompt text,
        added_at integer
    );'''