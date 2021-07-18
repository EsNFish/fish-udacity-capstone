

'''
Game
'''
from models.shared_db import db


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
            'genre': self.genre,
            'console': self.console}
