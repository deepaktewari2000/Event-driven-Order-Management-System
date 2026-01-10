import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def inspect():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.connect() as conn:
        # List tables
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = result.fetchall()
        print("Tables:", tables)

        # Check orders count if it exists
        try:
            result = await conn.execute(text("SELECT count(*) FROM orders"))
            print("Orders count:", result.scalar())
        except Exception as e:
            print("Orders table query failed:", e)

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(inspect())
