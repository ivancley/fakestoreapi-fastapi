from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 


DATABASE_URL = config("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,            
    max_overflow=40,
    pool_timeout=360,
    pool_recycle=3600,
    pool_pre_ping=True,
    echo=True,
    connect_args={
        "server_settings": {
            "timezone": "America/Sao_Paulo"
        }
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# O Celery precisa trabalhar com sincronismo 
SYNC_DATABASE_URL = config("DATABASE_URL").replace("+asyncpg", "")
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    pool_size=10,
    max_overflow=40,
    pool_timeout=360,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args={"options": "-c timezone=America/Sao_Paulo"}
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
