# utils/db.py
import csv

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from app.utils.settings import Config


def get_db_status(app):
    """Returns a tuple with the database connection status and HTTP code."""
    if app.db is None:
        return 'Error: Could not connect to the database.', 503
    return 'All systems operational.', 200


def init_db(app):
    """Initializes the database connection and optionally sets up the database."""
    print('Connecting to database...')
    try:
        # Attempt to connect to the database with a timeout
        client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=2000)
        client.server_info()  # Trigger a server info request to test the connection
        app.db = client[app.config['MONGODB_DB']]
        print('Database connection established.')

        # Initialize the database if configured to do so
        if app.config['DROP_COLLECTIONS']:
            setup_db(app.db)
            print('Database initialized.')
    except ServerSelectionTimeoutError as e:
        print(f'Error: Could not connect to the database: {e}')
        app.db = None


def setup_db(db):
    """Sets up the database by dropping collections and populating data."""
    if db is None:
        print('Database not initialized.')
        return

    print('Dropping collections...')
    db.drop_collection('users')
    db.drop_collection('items')
    db.drop_collection('recommendations')
    print('Collections dropped.')

    try:
        db.create_collection('users')
        print('Users collection initialized.')

        db.create_collection('recommendations')
        print('Recommendations collection initialized.')

        db.create_collection('items')
        db.items.create_index([('title', 'text')])


    except Exception as e:
        print(f'Error creating collection: {e}')

    # Populate the items collection from CSV data
    csv_file_path = 'recsys/datasets/movie_details.csv'
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            items = list(reader)  # More direct list conversion
            db.items.insert_many(items)
            print('Items collection initialized.')
    except FileNotFoundError:
        print(f'Error: File {csv_file_path} not found.')
    except Exception as e:
        print(f'Error: {e}')



