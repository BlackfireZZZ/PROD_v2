from flask import request, jsonify
from application import app
from application.db_countries import Countries
from flask import Blueprint


country_blueprint = Blueprint('country', __name__)


@country_blueprint.route('/', methods=['GET'])
def get_countries():
    region = request.args.get('region')
    if region:
        result = Countries().get_countries(region)
    else:
        result = Countries().get_countries()
    if result == 'Cannot connect to database':
        return jsonify({"reason": "Cannot connect to database"}), 500
    elif result == 'Country not found':
        return jsonify({"reason": "Country not found"}), 404
    else:
        return jsonify(result), 200


@country_blueprint.route("/<code>", methods=['GET'])
def get_country(code):
    result = Countries().get_country(code)
    if result == 'Country not found':
        return jsonify({"status": "Country not found"}), 404
    elif result == 'Cannot connect to database':
        return jsonify({"status": "Cannot connect to database"}), 500
    else:
        return jsonify(result), 200








