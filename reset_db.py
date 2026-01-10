import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def reset_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        # Disable foreign key checks temporarily to allow dropping in any order (PostgreSQL specific)
        await conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE")) 
        await conn.execute(text("DROP TYPE IF EXISTS orderstatus CASCADE"))
    
    print("Database reset complete.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_db())
