import logging

from flask import Flask, jsonify
from flask_cors import CORS

from app.routes.items import items_bp
from app.routes.recommendations import recommendations_bp
from app.routes.users import users_bp
from app.utils.recommender import precompute_svd
from app.utils.swagger import swagger_ui_blueprint

from app.utils.db import init_db, get_db_status
from app.utils.settings import Config

app = Flask(__name__)

app.config.from_object(Config)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

cors = CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/swagger/*": {"origins": "*"}
})
app.url_map.strict_slashes = False


@app.route('/', methods=['GET'])
def hello_world():
    (message, status_code) = get_db_status(app)
    return jsonify({"message": message}), status_code


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'message': 'The requested URL was not found on the server'}), 404


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'message': 'Internal server error'}), 500


app.register_blueprint(swagger_ui_blueprint)
app.register_blueprint(users_bp, url_prefix='/api')
app.register_blueprint(recommendations_bp, url_prefix='/api')
app.register_blueprint(items_bp, url_prefix='/api')

init_db(app)
precompute_svd()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
