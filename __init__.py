import os
from flask import Flask
import joblib


# create FLASK app
def create_app():
    app = Flask(__name__)

    from . import main_server
    app.register_blueprint(main_server.bp)
    # app.config.from_envvar('APP_CONFIG_FILE')

    return app