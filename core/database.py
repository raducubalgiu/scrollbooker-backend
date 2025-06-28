from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

#Load env
load_dotenv()

# Get the database URL from the env
DATABASE_URL=os.getenv("DATABASE_URL")

# Create an asynchronous engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

async_session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

#Dependecy to get a DB session
async def get_db():
    async with async_session_factory() as session:
        yield session