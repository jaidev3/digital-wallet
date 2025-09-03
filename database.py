from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


DATABASE_URL = "sqlite+aiosqlite:///./wallet.db"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    try:
        async with SessionLocal() as session:
            yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
