from flask_wtf import Form
from wtforms import TextField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length
from pygments.lexers import get_all_lexers
from .model import Paste


class CreatePasteForm(Form):
    name = TextField('Name', [Optional(), Length(0, 64)])
    content = TextAreaField('Content', [DataRequired()])
    expire_on = SelectField('Expiration time')
    syntax = SelectField('Syntax', default='text')

    def __init__(self, *args, **kwargs):
        super(CreatePasteForm, self).__init__(*args, **kwargs)
        self.expire_on.choices = [
            ('1hr', '1 hour'),
            ('1d', '1 day'),
            ('1w', '1 week'),
            ('1M', '1 month'),
            ('never', 'Never'),
        ]
        self.syntax.choices = []
        names = []
        for name, aliases, filetypes, mimetypes in get_all_lexers():
            names.append((aliases[0], name))

        names = sorted(names, key=lambda n: n[0])
        self.syntax.choices = names[:]
