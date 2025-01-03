from app import mongo

class ImageModel:
    @staticmethod
    def insert_image(data):
        return mongo.db.images.insert_one(data)

    @staticmethod
    def get_all_images():
        return list(mongo.db.images.find({}, {"_id": 0}))  # Exclude MongoDB's ObjectID
