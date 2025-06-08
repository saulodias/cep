import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from tqdm import tqdm
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Constants
CSV_DIR = os.getenv('CSV_DIR', 'csv')
SQL_DIR = os.getenv('SQL_DIR', 'sql')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10000'))

# Database connection constants
DB_NAME = os.getenv('DB_NAME', 'cep_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

def connect_to_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def import_states(conn):
    print("Importing states...")
    df = pd.read_csv(
        os.path.join(CSV_DIR, "states.csv"),
        dtype={'id': int, 'nome': str, 'uf': str},
        names=['id', 'nome', 'uf'],
        header=None
    )
    
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO estados (id, nome, uf)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                nome = EXCLUDED.nome,
                uf = EXCLUDED.uf
            """,
            [(row.id, row.nome, row.uf) for _, row in df.iterrows()]
        )
    conn.commit()

def import_cities(conn):
    print("Importing cities...")
    df = pd.read_csv(
        os.path.join(CSV_DIR, "cities.csv"),
        dtype={'id': int, 'nome': str, 'estado_id': int},
        names=['id', 'nome', 'estado_id'],
        header=None
    )
    
    print("\nCities being imported:")
    print(df[['id', 'nome', 'estado_id']].head().to_string())
    print(f"...and {len(df) - 5} more cities")
    
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO cidades (id, nome, estado_id)
            VALUES %s
            """,
            [(row.id, row.nome, row.estado_id) for _, row in df.iterrows()]
        )
    conn.commit()

def import_ceps(conn):
    # Get all state files (files named like 'XX.cepaberto_parte_*.csv')
    cep_files = [f for f in os.listdir(CSV_DIR) if re.match(r'^[a-z]{2}\.cepaberto_parte_\d+\.csv$', f)]
    
    # Calculate total number of rows to process
    total_rows = 0
    for file in cep_files:
        df = pd.read_csv(
            os.path.join(CSV_DIR, file),
            dtype={'cep': str},
            names=['cep', 'logradouro', 'complemento', 'bairro', 'cidade_id', 'estado_id'],
            header=None,
            nrows=1  # Just read the header to get the number of rows
        )
        total_rows += len(pd.read_csv(os.path.join(CSV_DIR, file), header=None))

    # Get state and city mappings once
    with conn.cursor() as cur:
        cur.execute("SELECT id, uf FROM estados")
        state_mapping = dict(cur.fetchall())
        cur.execute("SELECT id, nome FROM cidades")
        city_mapping = dict(cur.fetchall())
    
    # Process all files with a single progress bar
    with tqdm(total=total_rows, desc="Processing CEPs") as pbar:
        for file in sorted(cep_files):
            df = pd.read_csv(
                os.path.join(CSV_DIR, file),
                dtype={'cep': str},
                names=['cep', 'logradouro', 'complemento', 'bairro', 'cidade_id', 'estado_id'],
                header=None
            )
            
            # Add sigla and cidade columns based on IDs
            df['sigla'] = df['estado_id'].map(state_mapping)
            df['cidade'] = df['cidade_id'].map(city_mapping)
            
            # Process in batches
            total_batches = len(df) // BATCH_SIZE + (1 if len(df) % BATCH_SIZE else 0)
            
            for i in range(total_batches):
                start_idx = i * BATCH_SIZE
                end_idx = min((i + 1) * BATCH_SIZE, len(df))
                batch = df.iloc[start_idx:end_idx]
                
                values = [
                    (
                        row.cep,
                        row.logradouro if pd.notna(row.logradouro) else None,
                        row.complemento if pd.notna(row.complemento) else None,
                        row.bairro if pd.notna(row.bairro) else None,
                        int(row.cidade_id),
                        row.estado_id
                    )
                    for _, row in batch.iterrows()
                ]
                
                with conn.cursor() as cur:
                    execute_values(
                        cur,
                        """
                        INSERT INTO ceps (cep, logradouro, complemento, bairro, cidade_id, estado_id)
                        VALUES %s
                        ON CONFLICT (cep) DO UPDATE SET
                            logradouro = EXCLUDED.logradouro,
                            complemento = EXCLUDED.complemento,
                            bairro = EXCLUDED.bairro,
                            cidade_id = EXCLUDED.cidade_id,
                            estado_id = EXCLUDED.estado_id
                        """,
                        values
                    )
                conn.commit()
                pbar.update(len(batch))

def populate_search_table(conn):
    """Populate the search table from the normalized data"""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO ceps_search (cep, logradouro, complemento, bairro, cidade, uf)
            SELECT 
                c.cep,
                c.logradouro,
                c.complemento,
                c.bairro,
                ci.nome as cidade,
                e.uf
            FROM ceps c
            JOIN cidades ci ON c.cidade_id = ci.id
            JOIN estados e ON ci.estado_id = e.id
            ON CONFLICT (cep) DO UPDATE SET
                logradouro = EXCLUDED.logradouro,
                complemento = EXCLUDED.complemento,
                bairro = EXCLUDED.bairro,
                cidade = EXCLUDED.cidade,
                uf = EXCLUDED.uf;
        """)
    conn.commit()

def main():
    conn = connect_to_db()
    try:
        import_states(conn)
        import_cities(conn)
        import_ceps(conn)
        
        # Setup search vectors
        # with conn.cursor() as cur:
        #     cur.execute(open(os.path.join(SQL_DIR, 'setup_search_vector.sql'), 'r').read())
        # conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    main()