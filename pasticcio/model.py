from datetime import datetime
from .app import db


class Paste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    expire_on = db.Column(db.DateTime)
    content = db.Column(db.UnicodeText)
    syntax = db.Column(db.String(64))
    user = db.Column(db.String(64))
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def title(self):
        if self.name:
            return self.name
        else:
            return "#%d" % self.id

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64))
#     pastes = db.relationship('Paste', backref='user')
