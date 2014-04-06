from datetime import datetime, timedelta
from sqlalchemy import and_
from .app import db


class Paste(db.Model):
    expirations = {
        '1hr': timedelta(hours=1),
        '1d': timedelta(days=1),
        '1w': timedelta(weeks=1),
        '1M': timedelta(days=30),
        'never': None,
    }

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

    @classmethod
    def purge(cls):
        now = datetime.utcnow()
        query = cls.query.filter(and_(cls.expire_on != None,
                                      cls.expire_on < now))
        count = query.count()
        if count:
            query.delete()
            db.session.commit()
        return count

    @classmethod
    def get_expiration_date(self, value):
        delta = self.expirations.get(value)
        if delta is not None:
            return datetime.utcnow() + delta
        return delta

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64))
#     pastes = db.relationship('Paste', backref='user')
