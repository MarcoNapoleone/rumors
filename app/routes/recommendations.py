from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, request, jsonify, current_app

from app.utils.auth.auth import token_required
from app.utils.llm.llm_connector import explain_recommendation
from app.utils.s_big5 import calculate_ocens

recommendations_bp = Blueprint('recommendations', __name__)


# --- GET ---

@recommendations_bp.route('/recommendations/<recommendation_id>/explain', methods=['GET'])
@token_required
def get_recommendation_explanation(sub, recommendation_id):
    try:
        object_id = ObjectId(recommendation_id)
    except InvalidId:
        return jsonify({'message': 'Cannot find recommendation'}), 404

    recommendation = current_app.db.recommendations.find_one({'_id': object_id})

    if recommendation:
        if sub != recommendation['user_id']:
            return jsonify({'message': 'Forbidden'}), 403

        user = current_app.db.users.find_one({'_id': ObjectId(sub)})
        current_app.logger.info(f"User: {user}")

        if user is None:
            return jsonify({'message': 'Cannot find recommendation'}), 404

        if 'explanation' not in recommendation:
            item_to_recommend = current_app.db.items.find_one({'_id': ObjectId(recommendation['item_id'])})
            item_to_recommend = item_to_recommend['title']

            rated_items = []
            for rating in sorted(user['ratings'], key=lambda r: r['timestamp'], reverse=True)[:6]:
                try:
                    item = current_app.db.items.find_one({'_id': ObjectId(rating['item_id'])})
                    if item:
                        rated_items.append({
                            'title': item['title'],
                            'score': rating['score']
                        })
                except Exception as e:
                    current_app.logger.error(f"Error fetching item for rating: {rating} - {str(e)}")
                    continue  # Skip invalid or missing items


            if user['test_group'] == 'A':
                recommendation['explanation'] = explain_recommendation(rated_items, item_to_recommend,
                                                                       calculate_ocens(user['personality']))
            else:
                recommendation['explanation'] = explain_recommendation(rated_items, item_to_recommend)

            current_app.db.recommendations.update_one({'_id': object_id}, {'$set': recommendation})

        return jsonify({
            'recommendation_id': recommendation_id,
            'message': recommendation['explanation']['message']
        }), 200
    else:
        return jsonify({'message': 'Cannot find recommendation'}), 404


@recommendations_bp.route('/recommendations/<recommendation_id>/', methods=['GET'])
@token_required
def get_recommendation(sub, recommendation_id):
    try:
        object_id = ObjectId(recommendation_id)
    except InvalidId:
        return jsonify({'message': 'Cannot find recommendation'}), 404

    recommendation = current_app.db.recommendations.find_one({'_id': object_id})

    if recommendation:
        if sub != recommendation['user_id']:
            return jsonify({'message': 'Forbidden'}), 403

        recommendation['_id'] = str(recommendation['_id'])
        return jsonify(recommendation), 200
    else:
        return jsonify({'message': 'Cannot find recommendation'}), 404


# ---------------------------------------------- PUT ----------------------------------------------

# update recommendation to provide feedback
@recommendations_bp.route('/recommendations/<recommendation_id>/', methods=['PUT'])
@token_required
def update_recommendation(sub, recommendation_id):
    try:
        object_id = ObjectId(recommendation_id)
    except InvalidId:
        return jsonify({'message': 'Cannot find recommendation'}), 404

    try:
        current_time = datetime.now()
        recommendation = current_app.db.recommendations.find_one({'_id': object_id})
        if recommendation:

            if sub != recommendation['user_id']:
                return jsonify({'message': 'Forbidden'}), 403

            data = request.get_json()
            if 'comment' in data:
                recommendation['comment'] = data['comment']
            if 'convincing_score' in data:
                recommendation['convincing_score'] = data['convincing_score']
            if 'determinant_score' in data:
                recommendation['determinant_score'] = data['determinant_score']
            if 'resonates_score' in data:
                recommendation['resonates_score'] = data['resonates_score']
            if 'is_known' in data:
                recommendation['is_known'] = data['is_known']

            recommendation['updated_at'] = datetime.timestamp(current_time)
            recommendation['version'] += 1
            current_app.db.recommendations.update_one({'_id': object_id}, {'$set': recommendation})
            recommendation['_id'] = str(recommendation['_id'])
            return jsonify(recommendation), 200
        else:
            return jsonify({'message': 'Cannot find recommendation'}), 404
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'message': 'Error updating recommendation'}), 500
