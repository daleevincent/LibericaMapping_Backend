from app.database.mongo import db

class FarmModel:

    collection = db["farms"]

    @staticmethod
    def create(data):
        return FarmModel.collection.insert_one(data)

    @staticmethod
    def get_all():
        return list(FarmModel.collection.find())

    @staticmethod
    def get_by_owner(owner_id):
        return list(FarmModel.collection.find({"owner_id": owner_id}))