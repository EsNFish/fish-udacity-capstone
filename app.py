from flask import Flask

from .shared_db import setup_db
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
db = setup_db(app)

CORS(app, resources={r"*": {"origins": "*"}})
migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run()