from bson import ObjectId
from app.database.mongo import get_db

class TreeModel:

    @staticmethod
    def get_all():
        return list(get_db()['trees'].find())

    @staticmethod
    def get_by_farm(farm_id):
        return list(get_db()['trees'].find({'farmId': int(farm_id)}))

    @staticmethod
    def get_by_id(tree_id):
        return get_db()['trees'].find_one({'_id': ObjectId(tree_id)})

    @staticmethod
    def create(data):
        result = get_db()['trees'].insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def update(tree_id, data):
        data.pop('_id', None)
        result = get_db()['trees'].update_one(
            {'_id': ObjectId(tree_id)},
            {'$set': data}
        )
        return result.modified_count

    @staticmethod
    def delete(tree_id):
        result = get_db()['trees'].delete_one({'_id': ObjectId(tree_id)})
        return result.deleted_count

    @staticmethod
    def update_dna(tree_id, is_verified):
        result = get_db()['trees'].update_one(
            {'_id': ObjectId(tree_id)},
            {'$set': {'isDnaVerified': is_verified}}
        )
        return result.modified_count