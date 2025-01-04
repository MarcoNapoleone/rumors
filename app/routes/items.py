from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, request, jsonify, current_app

from app.models.Item import get_movie_poster, search_items, get_movie_genres

items_bp = Blueprint('items', __name__)


# --- GET ---

# /api/items/?query=item_param&sort=sort_param&limit=limit_param
@items_bp.route('/items', methods=['GET'], strict_slashes=False)
def get_items():
    # Retrieve query parameters
    query = request.args.get('query', '').strip()
    sort = request.args.get('sort', 'relevance')
    limit = int(request.args.get('limit', 10))
    page = int(request.args.get('page', 1))

    # Define allowed sort fields and ensure safety
    allowed_sort_fields = ['title', 'genres', 'imdbId', 'relevance']
    if sort not in allowed_sort_fields:
        sort = 'relevance'

    try:
        # Call the search_items function
        items = search_items(query, sort, limit, page)
        return jsonify(items)

    except RuntimeError as e:
        # Handle errors returned from the search_items function
        return jsonify({'error': str(e)}), 500


@items_bp.route('/items/<item_id>', methods=['GET'])
def get_item(item_id):
    try:
        object_id = ObjectId(item_id)
    except InvalidId:
        return jsonify({'message': 'Cannot find item'}), 404
    item = current_app.db.items.find_one({'_id': object_id})

    if item:
        item['_id'] = str(item['_id'])
        item['poster_path'] = get_movie_poster(item.get('poster_path'))
        item['genres'] = get_movie_genres(item.get('genres'))

        return jsonify(item), 200
    else:
        return jsonify({'message': 'Cannot find item'}), 404


@items_bp.route('/items/<item_id>/ratings', methods=['GET'])
def get_item_ratings(item_id):
    try:
        object_id = ObjectId(item_id)
    except InvalidId:
        return jsonify({'message': 'Cannot find item'}), 404

    item = current_app.db.items.find_one({'_id': object_id})
    if item:
        user_ratings = current_app.db.users.find({'ratings.item_id': str(object_id)})
        ratings = []
        for user in user_ratings:
            for rating in user['ratings']:
                if rating['item_id'] == str(object_id):
                    ratings.append({
                        'user_id': str(user['_id']),
                        'score': rating['score'],
                        'timestamp': rating['timestamp']
                    })
        return jsonify(ratings), 200
    else:
        return jsonify({'message': 'Cannot find item'}), 404

