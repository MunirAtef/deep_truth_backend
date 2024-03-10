from flask import Flask
from backend.mongodb_connection import MongoDB
from backend.routers.auth_router import auth_blueprint
from backend.routers.check_file_router import check_image_blueprint
from backend.routers.history_router import history_blueprint


app: Flask = Flask(__name__)


def register_routes():
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(check_image_blueprint, url_prefix='/image')
    app.register_blueprint(history_blueprint, url_prefix='/history')


@app.get("/")
def root():
    return "Hi there, I'm Munir the dev of this backend"


def run_server() -> None:
    connection_succeed = MongoDB.mongo_dp_connect()

    # # run this 2 lines if you need to clear the database
    # MongoDB.users.delete_many({})
    # MongoDB.history.delete_many({})

    if connection_succeed:
        register_routes()
        app.run(port=3000)


if __name__ == "__main__":
    run_server()
