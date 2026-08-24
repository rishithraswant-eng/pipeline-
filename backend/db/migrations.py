import asyncio
import aiosqlite
import os
import sys

# Ensure the parent directory is in sys.path so we can import schema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.db.schema import ORDERED_TABLES

from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.environ.get("SQLITE_DB_PATH", "/data/phantasm.db")
# Convert relative paths properly for local dev if needed
if DB_PATH.startswith("/data"):
    # If running locally on windows without docker for the backend, map /data to local ./data
    # For robust local dev, let's normalize this.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    DB_PATH = os.path.join(project_root, "data", "phantasm.db")

async def run_migrations():
    print(f"Applying migrations to database: {DB_PATH}")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Pragma setup as specified
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA synchronous=NORMAL;")
        await db.execute("PRAGMA cache_size=-64000;")
        await db.execute("PRAGMA foreign_keys=ON;")
        
        for table_sql in ORDERED_TABLES:
            try:
                await db.execute(table_sql)
            except Exception as e:
                print(f"Error executing table creation: {e}")
                print(f"SQL was: {table_sql}")
                sys.exit(1)
                
        await db.commit()
    print("Migrations complete. All 15 tables present.")

if __name__ == "__main__":
    asyncio.run(run_migrations())
