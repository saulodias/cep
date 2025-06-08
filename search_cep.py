import argparse
import os
from typing import Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv



# Load environment variables
load_dotenv()

# Database connection parameters from environment variables
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'cep_database'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def read_sql_file(filename: str) -> str:
    """Read SQL from a file"""
    with open(os.path.join(os.path.dirname(__file__), 'sql', filename), 'r', encoding='utf-8') as f:
        return f.read()

def prepare_tsquery(text: str) -> str:
    """Helper function to prepare text for tsquery"""
    if not text:
        return None
    return text.strip()

class CEPSearcher:
    def __init__(self):
        if not DB_PARAMS['password']:
            raise ValueError("Database password not set. Please set DB_PASSWORD in your environment variables.")
        self.conn = psycopg2.connect(**DB_PARAMS)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    
    def search_by_cep(self, cep: str) -> Optional[Dict]:
        """Busca endereço pelo número do CEP"""
        # Remove caracteres não numéricos do CEP
        cep = ''.join(filter(str.isdigit, cep))
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    cep,
                    logradouro,
                    complemento,
                    bairro,
                    cidade,
                    uf as estado
                FROM ceps_search
                WHERE cep = %s
            """, (cep,))
            
            result = cur.fetchone()
            return dict(result) if result else None

    def search_by_address(self, logradouro: str, limit: int = 10) -> List[Dict]:
        """Busca endereços usando full-text search"""
        logradouro_query = prepare_tsquery(logradouro)
        print(f"Debug: Original query: {logradouro}")
        print(f"Debug: Prepared query: {logradouro_query}")
        if not logradouro_query:
            return []
        
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Execute search query
            cur.execute("""
                SELECT 
                    cep,
                    logradouro,
                    complemento,
                    bairro,
                    cidade,
                    uf,
                    ts_rank(search_vector, plainto_tsquery('address_pt', 
                        normalize_address_numbers(%s))) as rank
                FROM ceps_search
                WHERE search_vector @@ plainto_tsquery('address_pt', 
                    normalize_address_numbers(%s))
                ORDER BY rank DESC
                LIMIT %s
            """, (logradouro_query, logradouro_query, limit))
            return [dict(r) for r in cur.fetchall()]

def main():
    """Command-line interface for CEP search"""
    parser = argparse.ArgumentParser(description='Search Brazilian postal codes (CEP)')
    parser.add_argument('--cep', help='Search by CEP number')
    parser.add_argument('--logradouro', help='Search by street name')
    parser.add_argument('--cidade', help='Filter by city name')
    parser.add_argument('--estado', help='Filter by state name or abbreviation')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of results')
    
    args = parser.parse_args()
    
    try:
        with CEPSearcher() as searcher:
            if args.cep:
                result = searcher.search_by_cep(args.cep)
                if result:
                    print("\nCEP encontrado:")
                    for k, v in result.items():
                        print(f"{k}: {v}")
                else:
                    print("\nCEP não encontrado")
            
            elif args.logradouro:
                results = searcher.search_by_address(
                    args.logradouro,
                    args.cidade,
                    args.estado,
                    args.limit
                )
                if results:
                    print(f"\nEncontrados {len(results)} endereços:")
                    for r in results:
                        print("\n" + "-"*50)
                        for k, v in r.items():
                            print(f"{k}: {v}")
                else:
                    print("\nNenhum endereço encontrado")
            
            else:
                parser.print_help()
    except ValueError as e:
        print(f"Error: {e}")
    except psycopg2.Error as e:
        print(f"Database error: {e}")

if __name__ == '__main__':
    main() 