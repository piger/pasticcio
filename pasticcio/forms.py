from datetime import datetime
from flask_wtf import Form
from wtforms import TextField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length
from pygments.lexers import get_all_lexers
from .app import app
from .model import Paste


class CreatePasteForm(Form):
    name = TextField('Name', [Optional(), Length(0, 64)])
    content = TextAreaField('Content', [DataRequired()])
    expire_on = SelectField('Expiration time')
    syntax = SelectField('Syntax', default='text')

    def get_expiration_date(self):
        delta = Paste.expirations.get(self.expire_on.data)[0]
        if delta is not None:
            return datetime.utcnow() + delta
        return delta

    def __init__(self, *args, **kwargs):
        super(CreatePasteForm, self).__init__(*args, **kwargs)
        # sort the dictionary of expiration times by length and create a list
        # of tuples: [(key, (timedelta, label)), ...]
        expirations = sorted(Paste.expirations.iteritems(),
                             key=lambda e: e[1][0],
                             reverse=True)
        # keep only the key and the label
        expirations = [(x[0], x[1][1]) for x in expirations]
        app.logger.debug("exp = %r", expirations)
        self.expire_on.choices = expirations[:]

        self.syntax.choices = []
        names = []
        for name, aliases, filetypes, mimetypes in get_all_lexers():
            names.append((aliases[0], name))

        names = sorted(names, key=lambda n: n[0])
        self.syntax.choices = names[:]
