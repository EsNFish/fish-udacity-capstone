from flask import Flask

from .models.console_model import Console
from .models.shared_db import setup_db
from .models.game_model import Game
from flask_migrate import Migrate

app = Flask(__name__)
# app.config.from_object('config')
db = setup_db(app)

migrate = Migrate(app, db)

new_game = Game('test', 'test')
new_game.insert()

new_console = Console('test', 'test')
new_console.insert()

if __name__ == '__main__':
    app.run()