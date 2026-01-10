
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def verify():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result.fetchall()]
        print("Tables found:", tables)
        
        if "users" in tables and "orders" in tables:
            print("SUCCESS: 'users' and 'orders' tables exist.")
        else:
            print("FAILURE: Missing tables.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify())
