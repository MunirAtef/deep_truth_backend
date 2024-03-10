import time

from backend.mongodb_connection import MongoDB


class HistoryFileModel:
    def __init__(self, file_name, user_id, result):
        self.file_name = file_name
        self.user_id = user_id
        self.date = int(time.time())
        self.result = result

    def to_json(self):
        return {
            "filename": self.file_name,
            "date": self.date,
            "user_id": self.user_id,
            "result": self.result
        }

    def save_to_db(self):
        inserted_json = self.to_json()
        MongoDB.history.insert_one(inserted_json)
        return inserted_json

    @staticmethod
    def get_user_file(user_id: str):
        result = MongoDB.history.find({"user_id": user_id})
        print(result)
        optimized = []
        for file in result:
            file_id = str(file["_id"])
            del file["_id"]
            file["id"] = file_id
            optimized.append(file)
        return optimized

    @staticmethod
    def delete_file(user_id: str, filename: str) -> int:
        result = MongoDB.history.delete_one({"user_id": user_id, "filename": filename})
        return result.deleted_count

    @staticmethod
    def delete_user_files(user_id: str) -> int:
        result = MongoDB.history.delete_many({"user_id": user_id})
        return result.deleted_count
