import os
import shutil
import subprocess
import sys

def get_postgres_share_dir():
    """Get PostgreSQL's share directory path"""
    try:
        # Try to get the path from pg_config
        result = subprocess.run(['pg_config', '--sharedir'], capture_output=True, text=True)
        if result.returncode == 0:
            return os.path.join(result.stdout.strip(), 'tsearch_data')
    except FileNotFoundError:
        pass
    
    # Default paths to check
    default_paths = [
        r'C:\Program Files\PostgreSQL\17\share\tsearch_data',
        r'C:\Program Files\PostgreSQL\16\share\tsearch_data',
        r'C:\Program Files\PostgreSQL\15\share\tsearch_data',
        '/usr/share/postgresql/tsearch_data',
        '/usr/local/share/postgresql/tsearch_data',
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    
    return None

def setup_dictionary():
    """Copy the address_pt.syn file to PostgreSQL's tsearch_data directory"""
    # Get source file path
    source_file = os.path.join(os.path.dirname(__file__), 'address_pt.syn')
    if not os.path.exists(source_file):
        print(f"Error: Could not find {source_file}")
        return False
    
    # Get PostgreSQL share directory
    target_dir = get_postgres_share_dir()
    if not target_dir:
        print("Error: Could not find PostgreSQL's tsearch_data directory")
        return False
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Copy the file
    target_file = os.path.join(target_dir, 'address_pt.syn')
    try:
        shutil.copy2(source_file, target_file)
        print(f"Successfully copied {source_file} to {target_file}")
        return True
    except PermissionError:
        print(f"Error: Permission denied. Try running the script as administrator/sudo")
        return False
    except Exception as e:
        print(f"Error copying file: {e}")
        return False

if __name__ == "__main__":
    if not setup_dictionary():
        sys.exit(1)
    print("Dictionary setup complete") 