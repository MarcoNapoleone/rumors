from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, request, jsonify, current_app, abort

from app.utils.AB_testing import get_balanced_ab_group
from app.utils.auth.auth import get_jwt, token_required, firewall
from app.utils.recommender import get_recommendations
from app.utils.s_big5 import calculate_ocens

users_bp = Blueprint('users', __name__)


# ---------------------------------------------- GET ----------------------------------------------

@users_bp.route('/users', methods=['GET'])
@firewall
def get_users():
    users = list(current_app.db.users.find())
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify(users)


@users_bp.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    try:
        # Convert user_id to ObjectId
        object_id = ObjectId(user_id)
    except InvalidId:
        # If user_id is not a valid ObjectId, return a 404 error
        return jsonify({'message': 'Cannot find user'}), 404

    # Try to find the user in the database
    user = current_app.db.users.find_one({'_id': object_id})
    if user:
        # If user is found, convert ObjectId to string and return user data
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    else:
        # If user is not found, return a 404 error
        return jsonify({'message': 'Cannot find user'}), 404


@users_bp.route('/users/<user_id>/ratings', methods=['GET'])
@token_required
def get_user_ratings(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    try:
        # Convert user_id to ObjectId
        object_id = ObjectId(user_id)
    except InvalidId:
        # If user_id is not a valid ObjectId, return a 404 error
        abort(404, description="User not found")

    # Try to find the user in the database
    user = current_app.db.users.find_one({'_id': object_id})
    if user:
        ratings = user['ratings']
        return jsonify(ratings), 200
    else:
        # If user is not found, return a 404 error
        abort(404, description="User not found")


@users_bp.route('/users/<user_id>/ocean', methods=['GET'])
@token_required
def get_user_ocens(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    try:
        # Convert user_id to ObjectId
        object_id = ObjectId(user_id)
    except InvalidId:
        # If user_id is not a valid ObjectId, return a 404 error
        abort(404, description="User not found")

    # Try to find the user in the database
    user = current_app.db.users.find_one({'_id': object_id})
    if user:
        # If user is found, and personality is not empty, return ocens
        if 'personality' in user and user['personality']:
            return calculate_ocens(user['personality']), 200
        else:
            return jsonify({'message': 'Personality scores not found'}), 404
    else:
        # If user is not found, return a 404 error
        abort(404, description="User not found")


@users_bp.route('/users/<user_id>/recommendations', methods=['GET'])
@token_required
def get_user_recommendation(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        abort(404, description="User not found")

    # Find the user in the database
    user = current_app.db.users.find_one({'_id': object_id})
    if not user:
        abort(404, description="User not found")

    # Retrieve the user's ratings
    ratings = user.get('ratings', [])
    if not ratings:
        return jsonify({'message': 'No ratings found'}), 404

    ratings = sorted(ratings, key=lambda x: x['timestamp'], reverse=True)[:6]

    # Fetch items based on the last 6 ratings
    item_ids = [ObjectId(rating['item_id']) for rating in ratings]
    items = list(current_app.db.items.find({'_id': {'$in': item_ids}}))

    #Dict where the key is the movieLensId and the value is the rating
    items = {item['movieLensId']: rating['score'] for item in items for rating in ratings if item['_id'] == ObjectId(rating['item_id'])}

    try:
        current_time = datetime.now()
        # Get recommendations based on the items
        recommendations = []
        res = get_recommendations(items)
        for r in res:
            matching_item = current_app.db.items.find_one({'movieLensId': r['movieLensId']})
            if matching_item:
                recommendation = {
                    'item_id': str(matching_item['_id']),
                    'user_id': user_id,
                    'pred_score': r['pred_score'],
                    'timestamp': datetime.timestamp(current_time),
                    'created_at': datetime.timestamp(current_time),
                    'updated_at': datetime.timestamp(current_time),
                    'version': 1
                }
                # Insert the recommendation into the database if it does not already exist by user and item
                # else update the existing recommendation
                existing_recommendation = current_app.db.recommendations.find_one(
                    {'user_id': user_id, 'item_id': recommendation['item_id']})
                if existing_recommendation:
                    current_app.db.recommendations.update_one(
                        {'_id': object_id},
                        {'$set': {'updated_at': datetime.timestamp(current_time)}}
                    )
                    recommendation['_id'] = str(existing_recommendation['_id'])

                else:
                    insert_result = current_app.db.recommendations.insert_one(recommendation)
                    recommendation['_id'] = str(insert_result.inserted_id)
                recommendations.append(recommendation)
        return jsonify(recommendations), 200

    except Exception as e:
        current_app.logger.error(f"Error generating recommendations: {e}")
        return jsonify({'error': 'Failed to generate recommendations'}), 500


# ---------------------------------------------- POST ----------------------------------------------

@users_bp.route('/users', methods=['POST'])
def add_new_user():
    # Parse JSON data from the request
    data = request.get_json()
    current_time = datetime.now()
    # Construct the user object with default values where necessary
    user = {
        'browser': data.get('browser'),
        'os': data.get('os'),
        'language': data.get('language'),
        'ratings': data.get('ratings', []),
        "test_group": get_balanced_ab_group(),
        'created_at': datetime.timestamp(current_time),
        'updated_at': datetime.timestamp(current_time),
        'version': 1
    }

    try:
        # Insert the new user into the database
        user_id = current_app.db.users.insert_one(user).inserted_id
    except Exception as e:
        # Handle database insertion errors
        current_app.logger.error(f"Error inserting new user: {e}")
        return jsonify({'error': 'Failed to add new user'}), 400

    # Convert the ObjectId to a string for JSON serialization
    user['_id'] = str(user_id)

    # Generate the JWT for the new user
    token = get_jwt({'sub': str(user_id)})

    return jsonify({'user': user, 'token': token}), 201


@users_bp.route('/users/<user_id>/ratings', methods=['POST'])
@token_required
def add_user_rating(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403
    data = request.get_json()
    current_time = datetime.now()

    # Validate the input data
    if not data:
        return jsonify({'message': 'No input data provided'}), 400
    if 'item_id' not in data:
        return jsonify({'message': 'Missing item_id'}), 400
    if data.get('score') is not None:
        if not isinstance(data['score'], int) or data['score'] < 1 or data['score'] > 5:
            return jsonify({'message': 'Invalid rating value'}), 400

    # check if item_id exists
    try:
        ObjectId(data['item_id'])
    except InvalidId:
        return jsonify({'message': 'Invalid item_id'}), 400

    rating = {
        'item_id': data['item_id'],
        'score': data['score'] if 'score' in data else None,
        'timestamp': datetime.timestamp(datetime.now()),
        'created_at': datetime.timestamp(current_time),
        'updated_at': datetime.timestamp(current_time),
        'version': 1,
    }

    try:
        # Insert the new rating into the database, using the user_id to identify the user, set updated_at and version
        current_app.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$push': {'ratings': rating},
             '$set': {'updated_at': datetime.timestamp(current_time), 'version': data.get('version', 1) + 1}}
        )
    except Exception as e:
        # Handle database insertion errors
        current_app.logger.error(f"Error inserting new rating: {e}")
        return jsonify({'error': 'Failed to add new rating'}), 400

    return jsonify(rating), 201


# ---------------------------------------------- PUT ----------------------------------------------
@users_bp.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({'message': 'Invalid user_id'}), 400

    # Retrieve and validate input data
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    # Filter out any fields that should not be updated
    disallowed_fields = ['_id', 'user_id', 'password', 'created_at', 'updated_at', 'version', 'deleted_at', 'ratings',
                         'recommendations', 'test_group']
    update_data = {key: value for key, value in data.items() if key not in disallowed_fields}
    update_data['updated_at'] = datetime.timestamp(datetime.now())
    update_data['version'] = current_app.db.users.find_one({'_id': object_id})['version'] + 1

    if not update_data:
        return jsonify({'message': 'No valid fields to update'}), 400

    try:
        # Update user document in the database
        result = current_app.db.users.update_one({'_id': object_id}, {'$set': update_data})
        if result.matched_count == 0:
            return jsonify({'message': 'User not found'}), 404

        # Retrieve the updated user document
        user = current_app.db.users.find_one({'_id': object_id})
        if not user:
            return jsonify({'message': 'User not found after update'}), 404

        user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
        return jsonify({'message': 'User updated successfully', 'user': user}), 200

    except Exception as e:
        current_app.logger.error(f"Error updating user: {e}")
        return jsonify({'message': 'Internal server error'}), 500


@users_bp.route('/users/<user_id>/ratings', methods=['PUT'])
@token_required
def update_user_rating(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({'message': 'Invalid user_id'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    if 'item_id' not in data:
        return jsonify({'message': 'Missing item_id'}), 400

    if data.get('score') is not None:
        if not isinstance(data['score'], int) or data['score'] < 1 or data['score'] > 5:
            return jsonify({'message': 'Invalid rating value'}), 400

    rating = {
        'item_id': data['item_id'],
        'score': data['score'] if 'score' in data else None,
        'timestamp': datetime.timestamp(datetime.now())
    }

    try:
        current_app.db.users.update_one(
            {'_id': object_id, 'ratings.item_id': data['item_id']},
            {'$set': {'ratings.$.score': rating['score'], 'ratings.$.timestamp': rating['timestamp']}}
        )
    except Exception as e:
        current_app.logger.error(f"Error updating rating: {e}")
        return jsonify({'error': 'Failed to update rating'}), 400

    return jsonify(rating), 200


# ---------------------------------------------- DELETE ----------------------------------------------

@users_bp.route('/users/<user_id>/ratings', methods=['DELETE'])
@token_required
def delete_user_ratings(sub, user_id):
    if sub != user_id:
        return jsonify({'message': 'Forbidden'}), 403

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        return jsonify({'message': 'Invalid user_id'}), 400

    try:

        current_app.db.users.update_one(
            {'_id': object_id},
            {'$set': {'ratings': []}}
        )
    except Exception as e:
        current_app.logger.error(f"Error deleting ratings: {e}")
        return jsonify({'error': 'Failed to delete ratings'}), 400

    return jsonify({'message': 'Ratings deleted successfully'}), 200
