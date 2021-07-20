from flask import Flask

from .shared_db import setup_db
from flask_migrate import Migrate

app = Flask(__name__)
db = setup_db(app)

migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run()