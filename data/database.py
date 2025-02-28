from pymongo.mongo_client import MongoClient
from sqlalchemy import create_engine
from config.settings import BASE_DE_DATOS, MONGODB_URI, MONGODB_DB_NAME, PG_DATABASE_URL


def init_connections():
    """Initialize database connections based on configuration.

    Returns:
        tuple: (mongodb_client, sqlalchemy_engine)
    """
    # MongoDB connection
    client = MongoClient(MONGODB_URI)

    # PostgreSQL connection
    engine = create_engine(PG_DATABASE_URL)

    return client, engine


def get_db(client):
    """Get MongoDB database instance.

    Args:
        client: MongoDB client connection

    Returns:
        MongoDB database instance
    """
    return client[MONGODB_DB_NAME]


def close_connections(client, engine):
    """Close all database connections.

    Args:
        client: MongoDB client
        engine: SQLAlchemy engine
    """
    if client:
        client.close()

    if engine:
        engine.dispose()
