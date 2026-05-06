import asyncio
from sqlalchemy import inspect
from app.db.session import engine

async def check_tables():
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        print(f"Tables in database: {tables}")
        if "merchants" in tables:
            print("SUCCESS: 'merchants' table exists.")
        else:
            print("FAILURE: 'merchants' table not found.")

if __name__ == "__main__":
    asyncio.run(check_tables())
