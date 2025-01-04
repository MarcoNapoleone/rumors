import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    DEBUG = os.environ.get("DEBUG", "True").lower() in ["true", "1", "yes"]
    FLASK_ENV = os.environ.get("FLASK_ENV")

    # TMDB settings
    TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "YOUR_API_KEY")

    # JWT settings
    JWT_SECRET = os.environ.get('JWT_SECRET', 'rumors_secret_key')
    JWT_ISSUER = os.environ.get('JWT_ISSUER', 'rumors-api')
    JWT_AUDIENCE = os.environ.get('JWT_AUDIENCE', 'rumors-users')
    JWT_EXPIRATION = int(os.environ.get('JWT_EXPIRATION', 7200))

    # IP addresses that do not require authentication
    NO_AUTH_IPS = os.environ.get('NO_AUTH_IPS', '').split(',')

    # MongoDB settings
    MONGODB_HOST = os.environ.get("MONGODB_HOST", "mongo")
    MONGODB_DB = os.environ.get("MONGODB_DB", "app")
    MONGODB_USER = os.environ.get("MONGODB_USER", "app")
    MONGODB_PASS = os.environ.get("MONGODB_PASS", "root")
    DROP_COLLECTIONS = os.environ.get("DROP_COLLECTIONS", "False").lower() in ["true", "1", "yes"]
    if FLASK_ENV == 'dev':
        MONGODB_PORT = os.environ.get("MONGODB_PORT", "27017")
        MONGODB_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DB}"
    elif FLASK_ENV == 'prod':
        MONGODB_URI = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}/{MONGODB_DB}?retryWrites=true&w=majority"

    # LLM settings
    OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
    LLM_URL = os.getenv("LLM_URL")
    LLM_MODEL = os.environ.get("LLM_MODEL")
    LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", 0)) # Default temperature
    LLM_ENDPOINT_TYPE = os.environ.get("LLM_ENDPOINT_TYPE")

    # Recommender settings
    RATINGS_PATH = os.environ.get("RATINGS_PATH", "recsys/datasets/ratings.csv")






