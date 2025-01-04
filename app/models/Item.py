import ast
import re
from typing import List, Optional

from flask import current_app, jsonify
from pydantic import BaseModel
from pymongo import ASCENDING
from pymongo.errors import OperationFailure
from requests import get, exceptions


def get_movie_poster(image_id):
    return "https://image.tmdb.org/t/p/w500" + image_id

def get_movie_genres(genres):
    # Ensure that `genres` is a list of dictionaries. If it's a string, convert it to a list.
    if isinstance(genres, str):
        genres = ast.literal_eval(genres)

    # Check if `genres` is a list and each item is a dictionary with a 'name' key
    if isinstance(genres, list) and all(isinstance(genre, dict) and 'name' in genre for genre in genres):
        return " | ".join([genre['name'] for genre in genres])
    else:
        return ""

def fetch_movie_info(movie_id):
    language = 'en-US'
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language={language}&external_source=imdb_id"

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer " + current_app.config['TMDB_API_KEY']
    }

    try:
        response = get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except (exceptions.HTTPError, KeyError, Exception) as e:
        current_app.logger.error(f"Error fetching movie info: {e}")
        RuntimeError(f"Error fetching movie info: {e}")
        return None

from flask import current_app
from pymongo.errors import OperationFailure
from pymongo import ASCENDING, DESCENDING
import re

def search_items(query, sort='relevance', limit=10, page=1):
    """
    A modern, simple search engine function to query a MongoDB collection, with enhanced title matching.

    Args:
        query (str): Search query string.
        sort (str): Field to sort by ('relevance', 'title', or 'imdbId'). Defaults to 'relevance'.
        limit (int): Maximum number of results per page. Defaults to 10, capped at 100.
        page (int): Page number for pagination. Defaults to 1.

    Returns:
        list: List of search results with processed fields.
    """
    limit = min(max(int(limit), 1), 100)  # Ensure limit is between 1 and 100
    page = max(int(page), 1)
    sort = sort if sort in ['relevance', 'title', 'imdbId'] else 'relevance'
    db = current_app.db

    search_filter = {}
    projection = {}
    boosted_items = []

    if query:
        tokens = query.split()
        query_pattern = '.*' + '.*'.join(re.escape(token) for token in tokens) + '.*'

        # Create a case-insensitive exact title pattern
        exact_title_pattern = f'^{re.escape(query)}$'

        if 'title_text' in db.list_collection_names():
            # Use text search with weighted fields
            db.command('text', 'items', search=query, weights={
                'title': 10,      # Highest weight for title
                'overview': 3,    # Medium weight for overview
                'genres': 2,      # Lower weight for genres
                'production_companies': 1  # Lowest weight for companies
            })

            search_filter = {
                '$or': [
                    # Exact title match (highest priority)
                    {'title': {'$regex': exact_title_pattern, '$options': 'i'}},
                    # Text search for all fields
                    {'$text': {'$search': query}}
                ]
            }

            # Include text score in projection
            projection['score'] = {'$meta': 'textScore'}

        else:
            # Fallback to regex search with weighted scoring
            search_filter['$or'] = [
                # Exact title match (highest priority)
                {'title': {'$regex': exact_title_pattern, '$options': 'i'}},
                # Partial title match (high priority)
                {'title': {'$regex': query_pattern, '$options': 'i'}},
                # Other fields with lower priority
                {'overview': {'$regex': query_pattern, '$options': 'i'}},
                {'genres': {'$regex': query_pattern, '$options': 'i'}},
                {'production_companies': {'$regex': query_pattern, '$options': 'i'}}
            ]

    skip = (page - 1) * limit

    try:
        if sort == 'relevance':
            if 'score' in projection:
                # Use text score sorting with boosted exact matches
                pipeline = [
                    {'$match': search_filter},
                    {'$addFields': {
                        'exactMatch': {
                            '$cond': {
                                'if': {'$regexMatch': {
                                    'input': '$title',
                                    'regex': exact_title_pattern,
                                    'options': 'i'
                                }},
                                'then': 1000,  # Boost exact matches
                                'else': 0
                            }
                        }
                    }},
                    {'$sort': {
                        'exactMatch': -1,
                        'score': {'$meta': 'textScore'}
                    }},
                    {'$skip': skip},
                    {'$limit': limit}
                ]
                cursor = db.items.aggregate(pipeline)
            else:
                # Custom relevance scoring without text index
                pipeline = [
                    {'$match': search_filter},
                    {'$addFields': {
                        'relevanceScore': {
                            '$add': [
                                # Exact title match score
                                {'$cond': [
                                    {'$regexMatch': {
                                        'input': '$title',
                                        'regex': exact_title_pattern,
                                        'options': 'i'
                                    }},
                                    1000,
                                    0
                                ]},
                                # Partial title match score
                                {'$cond': [
                                    {'$regexMatch': {
                                        'input': '$title',
                                        'regex': query_pattern,
                                        'options': 'i'
                                    }},
                                    500,
                                    0
                                ]}
                            ]
                        }
                    }},
                    {'$sort': {'relevanceScore': -1}},
                    {'$skip': skip},
                    {'$limit': limit}
                ]
                cursor = db.items.aggregate(pipeline)
        else:
            # Standard sorting by title or imdbId
            sort_field = 'title' if sort == 'title' else 'imdbId'
            cursor = (db.items.find(search_filter, projection)
                      .sort([(sort_field, ASCENDING)])
                      .skip(skip)
                      .limit(limit))

        for item in cursor:
            item['_id'] = str(item['_id'])
            item['poster_path'] = get_movie_poster(item.get('poster_path'))
            item['genres'] = get_movie_genres(item.get('genres'))
            boosted_items.append(item)

        return boosted_items

    except OperationFailure as e:
        raise RuntimeError(f"Database operation failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An error occurred during search: {str(e)}")



class Movie(BaseModel):
    title: str
    genres: List[str] = []
    overview: Optional[str] = None
    release_date: Optional[str] = None
    poster_path: Optional[str] = None
    imdb_id: Optional[str] = None
    tmdb_id: Optional[str] = None
    movielens_id: Optional[str] = None
