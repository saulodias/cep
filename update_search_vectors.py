import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'cep_database'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def run_sql_file(conn, sql_file):
    """Execute a SQL file"""
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    with conn.cursor() as cur:
        cur.execute(sql_content)
        conn.commit()
    
    print(f"✓ Executed {sql_file}")

def main():
    """Main function - runs the master SQL setup"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("Setting up CEP search system with SQL files...")
        
        # Run the master setup file
        run_sql_file(conn, 'sql/setup_all.sql')
        
        print("Setup completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 