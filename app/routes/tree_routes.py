from flask import Blueprint, request, jsonify
from app.models.tree_model import TreeModel
from bson import ObjectId
import json

tree_bp = Blueprint('tree_bp', __name__)

def serialize(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    doc['_id'] = str(doc['_id'])
    return doc

# ── GET /trees/ — all trees or filter by farmId ──────────────────────────────
@tree_bp.route('/trees/', methods=['GET'])
def get_trees():
    farm_id = request.args.get('farmId')
    if farm_id:
        trees = TreeModel.get_by_farm(int(farm_id))
    else:
        trees = TreeModel.get_all()
    return jsonify([serialize(t) for t in trees]), 200

# ── GET /trees/<id> — single tree ─────────────────────────────────────────────
@tree_bp.route('/trees/<tree_id>', methods=['GET'])
def get_tree(tree_id):
    tree = TreeModel.get_by_id(tree_id)
    if not tree:
        return jsonify({'error': 'Tree not found'}), 404
    return jsonify(serialize(tree)), 200

# ── POST /trees/ — create new tree ────────────────────────────────────────────
@tree_bp.route('/trees/', methods=['POST'])
def create_tree():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required = ['treeId', 'farmId', 'coordinates', 'isDnaVerified']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    inserted_id = TreeModel.create(data)
    return jsonify({'message': 'Tree created', '_id': inserted_id}), 201

# ── PUT /trees/<id> — update tree ─────────────────────────────────────────────
@tree_bp.route('/trees/<tree_id>', methods=['PUT'])
def update_tree(tree_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    count = TreeModel.update(tree_id, data)
    if count == 0:
        return jsonify({'error': 'Tree not found or no changes'}), 404
    return jsonify({'message': 'Tree updated'}), 200

# ── PATCH /trees/<id>/dna — toggle DNA verification ───────────────────────────
@tree_bp.route('/trees/<tree_id>/dna', methods=['PATCH'])
def update_dna(tree_id):
    data = request.get_json()
    if 'isDnaVerified' not in data:
        return jsonify({'error': 'isDnaVerified field required'}), 400
    count = TreeModel.update_dna(tree_id, data['isDnaVerified'])
    if count == 0:
        return jsonify({'error': 'Tree not found'}), 404
    return jsonify({'message': 'DNA status updated'}), 200

# ── DELETE /trees/<id> — delete tree ──────────────────────────────────────────
@tree_bp.route('/trees/<tree_id>', methods=['DELETE'])
def delete_tree(tree_id):
    count = TreeModel.delete(tree_id)
    if count == 0:
        return jsonify({'error': 'Tree not found'}), 404
    return jsonify({'message': 'Tree deleted'}), 200