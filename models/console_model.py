

'''
Console
'''
from .shared_db import db


class Console(db.Model):
    __tablename__ = 'console'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    company = db.Column(db.String)

    def __init__(self, name, company=""):
        self.name = name
        self.company = company

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
