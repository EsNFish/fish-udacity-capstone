from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
import os

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Game
'''


class Game(db.Model):
    __tablename__ = 'Games'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    genre = Column(String)
    console = Column(String)

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
            'genre': self.genre,
            'console': self.console}