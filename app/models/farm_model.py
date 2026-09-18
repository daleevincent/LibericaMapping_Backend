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

    @staticmethod
    def get_by_id(farm_id):
        # Query by numeric id field — not MongoDB _id
        return FarmModel.get_collection().find_one({"id": int(farm_id)})

    @staticmethod
    def update(farm_id, data):
        data.pop("_id", None)  # remove _id to avoid immutable field error
        result = FarmModel.get_collection().update_one(
            {"id": int(farm_id)},
            {"$set": data}
        )
        return result.modified_count