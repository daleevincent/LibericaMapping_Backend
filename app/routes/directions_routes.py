from flask import Blueprint, request, jsonify
import requests
import os

directions_bp = Blueprint('directions_bp', __name__)

@directions_bp.route('/directions/', methods=['GET'])
def get_directions():
    origin      = request.args.get('origin')
    destination = request.args.get('destination')

    if not origin or not destination:
        return jsonify({'error': 'origin and destination required'}), 400

    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        return jsonify({'error': 'GOOGLE_MAPS_API_KEY not set'}), 500

    url = (
        f'https://maps.googleapis.com/maps/api/directions/json'
        f'?origin={origin}'
        f'&destination={destination}'
        f'&mode=driving'
        f'&key={api_key}'
    )

    resp = requests.get(url, timeout=15)
    return jsonify(resp.json())