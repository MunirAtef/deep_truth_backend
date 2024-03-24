import time

from bson import ObjectId
from backend.mongodb_connection import MongoDB

class ReqStatus:
    pending: str = "pending"
    accepted: str = "accepted"
    # removed: str = "removed"
    # undone: str = "undone"


class ConnectionModel:
    def __init__(self, requester_id: str, recipient_id: str, status=ReqStatus.pending):
        self.requester_id = ObjectId(requester_id)
        self.recipient_id = ObjectId(recipient_id)
        self.status = status
        self.pending_date = int(time.time())
        self.updating_date = None

    def to_json(self) -> dict[str, any]:
        return {
            "requester_id": self.requester_id,
            "recipient_id": self.recipient_id,
            "status": self.status,
            "pending_date": self.pending_date,
            "updating_date": self.updating_date
        }

    def validate(self):
        if self.requester_id == self.recipient_id:
            return {"message": "cannot_connect_to_yourself"}, 400
        doc = MongoDB.users.find_one({"_id": self.recipient_id})
        if not doc:
            return {"message": "recipient_not_found"}, 404

        condition = {
            "requester_id": self.requester_id,
            "recipient_id": self.recipient_id
        }

        existing_count = MongoDB.connections.count_documents(condition)
        if existing_count != 0:
            return {"message": "request_already_sent"}, 409

    def save(self):
        validation_msg = self.validate()
        if validation_msg:
            return validation_msg
        MongoDB.connections.insert_one(self.to_json())

    @staticmethod
    def outbound_requests(user_id: str):
        pipeline = [
            {"$match": {"requester_id": ObjectId(user_id), "status": ReqStatus.pending}},
            {"$lookup": {"from": "users", "localField": "recipient_id", "foreignField": "_id", "as": "recipient"}},
            {"$unwind": "$recipient"},
            {"$project": {
                "_id": 0,
                "user": {"id": {"$toString": "$recipient._id"},
                         "name": "$recipient.name", "email": "$recipient.email",
                         "profile_picture": "$recipient.profile_picture"},
                "status": 1,
                "pending_date": 1,
                "updating_date": 1
            }}
        ]
        return list(MongoDB.connections.aggregate(pipeline))

    @staticmethod
    def inbound_requests(user_id: str):
        pipeline = [
            {"$match": {"recipient_id": ObjectId(user_id), "status": ReqStatus.pending}},
            {"$lookup": {"from": "users", "localField": "requester_id", "foreignField": "_id", "as": "requester"}},
            {"$unwind": "$requester"},
            {"$project": {
                "_id": 0,
                "user": {"id": {"$toString": "$requester._id"},
                         "name": "$requester.name", "email": "$requester.email",
                         "profile_picture": "$requester.profile_picture"},
                "status": 1,
                "pending_date": 1,
                "updating_date": 1
            }}
        ]
        return list(MongoDB.connections.aggregate(pipeline))

    @staticmethod
    def accept(user_id: str, requester_id: str):
        query = {
            "requester_id": ObjectId(requester_id),
            "recipient_id": ObjectId(user_id),
            "status": {"$ne": ReqStatus.accepted}
        }
        update = {"status": ReqStatus.accepted, "updating_date": int(time.time())}
        result = MongoDB.connections.update_one(query, {"$set": update})

        return result.matched_count > 0

    @staticmethod
    def remove_request(user_id: str, requester_id: str):
        condition = {
            "requester_id": ObjectId(requester_id),
            "recipient_id": ObjectId(user_id)
        }
        MongoDB.connections.delete_one(condition)

    @staticmethod
    def undo_request(user_id: str, recipient_id: str):
        condition = {
            "requester_id": ObjectId(user_id),
            "recipient_id": ObjectId(recipient_id)
        }
        MongoDB.connections.delete_one(condition)

    @staticmethod
    def connections(user_id: str):
        user_id = ObjectId(user_id)
        query = {"$or": [{"requester_id": user_id}, {"recipient_id": user_id}], "status": ReqStatus.accepted}
        cond = {"if": {"$eq": ["$$requester_id", user_id]},
                "then": {"$eq": ["$_id", "$$recipient_id"]},
                "else": {"$eq": ["$_id", "$$requester_id"]}}

        pipeline = [
            {"$match": query},
            {"$lookup": {
                "from": "users",
                "let": {"requester_id": "$requester_id", "recipient_id": "$recipient_id"},
                "pipeline": [{"$match": {"$expr": {"$cond": cond}}}],
                "as": "user_lookup"
            }},
            {"$unwind": "$user_lookup"},
            {"$replaceRoot": {"newRoot": "$user_lookup"}},
            {"$project": {"_id": 0, "id": {"$toString": "$_id"}, "name": 1, "email": 1, "profile_picture": 1}}
        ]
        return list(MongoDB.connections.aggregate(pipeline))

    @staticmethod
    def get_relation(user_id: str, target_id: str):
        user_id = ObjectId(user_id)
        target_id = ObjectId(target_id)

        query = {"$or": [
            {"requester_id": user_id, "recipient_id": target_id},
            {"requester_id": target_id, "recipient_id": user_id}
        ]}
        projection = {
            "_id": 0,
            "requester_id": {"$toString": "$requester_id"},
            "recipient_id": {"$toString": "$recipient_id"},
            "status": 1,
            "pending_date": 1,
            "updating_date": 1
        }
        relation = MongoDB.connections.find_one(query, projection=projection)
        print(relation)
        return relation
