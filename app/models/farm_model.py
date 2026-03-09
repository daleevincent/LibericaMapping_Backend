from app.database.mongo import db as get_db
from app.database import mongo as mongo_module

class FarmModel:

    @staticmethod
    def get_collection():
        return mongo_module.db["farms"]

    @staticmethod
    def create(data):
        return FarmModel.get_collection().insert_one(data)

    @staticmethod
    def get_all():
        return list(FarmModel.get_collection().find())

    @staticmethod
    def get_by_owner(owner_id):
        return list(FarmModel.get_collection().find({"owner_id": owner_id}))