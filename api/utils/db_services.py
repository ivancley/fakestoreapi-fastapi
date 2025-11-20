from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 


DATABASE_URL = config("DATABASE_URL")

# Criar engine assíncrono apenas se o DATABASE_URL contiver +asyncpg
engine = None
AsyncSessionLocal = None

if "+asyncpg" in DATABASE_URL:
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
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
if "+psycopg2" not in SYNC_DATABASE_URL:
    if "postgresql://" in SYNC_DATABASE_URL:
        SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

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
    if AsyncSessionLocal is None:
        raise RuntimeError("AsyncSessionLocal não está configurado. Verifique se DATABASE_URL contém '+asyncpg'")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
