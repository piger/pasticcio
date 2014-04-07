import hashlib
import os
from datetime import datetime, timedelta
from flask import g, url_for
from sqlalchemy import and_
from pygments import highlight
from pygments.lexers import get_lexer_by_name, ClassNotFound
from pygments.formatters import HtmlFormatter
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        if self.expire_on is None:
            expire_on = None
        else:
            expire_on = self.expire_on.isoformat()
        paste_id = g.hashid.encrypt(self.id)
        rv = {
            'title': self.title,
            'created_on': self.created_on.isoformat(),
            'expire_on': expire_on,
            'syntax': self.syntax,
            'link': url_for('show_paste', paste_id=paste_id, _external=True),
            'paste_id': paste_id,
        }
        return rv

    @property
    def title(self):
        if self.name:
            return self.name
        else:
            return "#%d" % self.id

    @property
    def pretty_output(self):
        try:
            lexer = get_lexer_by_name(self.syntax)
            default_lexer = get_lexer_by_name('text')
            fmt = HtmlFormatter(linenos='table', anchorlinenos=True,
                                lineanchors='line')
            output = highlight(self.content, lexer, fmt)
        except ClassNotFound:
            output = highlight(self.content, default_lexer, fmt)

        return output

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    pastes = db.relationship('Paste', backref='user')
    api_key = db.relationship('APIKey', uselist=False, backref='user')

class APIKey(db.Model):
    key = db.Column(db.String(40), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self):
        self.key = hashlib.sha1(os.urandom(20)).hexdigest()
