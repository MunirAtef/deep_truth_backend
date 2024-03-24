from flask import Flask

from backend.mongodb_connection import MongoDB
from backend.routers.auth_router import auth_blueprint
from backend.routers.check_file_router import check_image_blueprint
from backend.routers.connection_router import connection_blueprint
from backend.routers.history_router import history_blueprint
from backend.routers.interaction_router import interact_blueprint
from backend.routers.profile_router import profile_blueprint

app: Flask = Flask(__name__)


def register_routes():
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(check_image_blueprint, url_prefix='/image')
    app.register_blueprint(history_blueprint, url_prefix='/history')
    app.register_blueprint(interact_blueprint, url_prefix='/interact')
    app.register_blueprint(profile_blueprint, url_prefix='/profile')
    app.register_blueprint(connection_blueprint, url_prefix='/connect')


@app.get("/")
def root():
    return "Hi there, I'm Munir the dev of this backend"


def run_server() -> None:
    connection_succeed = MongoDB.mongo_dp_connect()

    # ngrok http --domain=munir_atef.deep_truth 3000
    # https://precise-albacore-simply.ngrok-free.app

    # # run this 2 lines if you need to clear the database
    # MongoDB.users.delete_many({})
    # MongoDB.history.delete_many({})

    if connection_succeed:
        register_routes()
        # app.run(port=10000, host='0.0.0.0')
        # app.run(port=3000)
        # run_with_lt(app, subdomain="munir.atef")
        app.run(port=3000)
        print("running on port 3000")


if __name__ == "__main__":
    print("ngrok http --domain=precise-albacore-simply.ngrok-free.app 3000")
    run_server()
