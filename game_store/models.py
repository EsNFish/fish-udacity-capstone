from shared_db import db

default_name = "game_store"
default_path = "postgresql://test:test@{}/{}".format('localhost:5432', default_name)


def setup_db(app, database_path=default_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    return db

'''
Game
'''


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genre = db.Column(db.String)
    console = db.Column(db.String)

    def __init__(self, name, genre="", console=""):
        self.name = name
        self.genre = genre
        self.console = console

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'genre': self.genre,
            'console': self.console}