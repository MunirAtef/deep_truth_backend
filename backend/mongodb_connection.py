import os
from typing import Optional

from pymongo.database import Database
from dotenv import load_dotenv

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoDB:
    _db: Optional[Database] = None
    users = None
    history = None

    @staticmethod
    def mongo_dp_connect() -> bool:
        if MongoDB._db is not None:
            return True
        try:
            load_dotenv()

            client = MongoClient(os.getenv('MONGO_URI'), server_api=ServerApi('1'))
            try:
                client.admin.command('ping')

                print("Pinged your deployment. You successfully connected to MongoDB!")
            except Exception as e:
                print(e)

            MongoDB._db = client.get_database("DeepTruthDB")
            MongoDB.users = MongoDB._db.users
            MongoDB.history = MongoDB._db.history
            return True
        except RuntimeError:
            print("Exception in connecting with db")
            return False
