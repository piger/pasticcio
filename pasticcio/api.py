from flask import json, jsonify, abort, redirect, url_for, request, g
from flask.views import MethodView
from werkzeug import MultiDict
from pygments.lexers import guess_lexer
from .model import Paste, User, APIKey
from .app import app, db
from .views import decrypt_paste_id
from . import forms


def guess_syntax(text):
    lexer = guess_lexer(text)
    if lexer is not None:
        return lexer.aliases[0]
    else:
        return 'text'

class PasteAPI(MethodView):
    def _get_user(self):
        key = request.args.get('key')
        if key is None:
            abort(401)

        user = User.query.join(APIKey).filter(APIKey.key==key).first()
        if user is None:
            abort(401)

        return user

    def get(self, paste_id):
        _id = decrypt_paste_id(paste_id)
        if _id is None:
            abort(404)
        paste = Paste.query.get(_id)

        return jsonify(paste=paste.to_dict(), status='ok')

    def post(self):
        """Create a new Paste with the REST API.

        Query parameters:

        - key (str): the authentication key
        - guess (bool): enable lexer guessing for syntax highlight

        The JSON parameters are the same for the Paste creation form.
        """
        user = self._get_user()
        data = MultiDict(request.json)
        guessing = request.args.get('guess')

        form = forms.CreatePasteForm(data, csrf_enabled=False)
        if form.validate_on_submit():
            if guessing:
                syntax = guess_syntax(form.content.data)
            else:
                syntax = form.syntax.data
            expire_on = Paste.get_expiration_date(form.expire_on.data)
            paste = Paste(name=form.name.data,
                          content=form.content.data,
                          syntax=syntax,
                          expire_on=expire_on,
                          user=user)
            db.session.add(paste)
            db.session.commit()
            db.session.refresh(paste)
        
            return jsonify(status='ok', paste=paste.to_dict()), 201

        abort(400)

    def delete(self, paste_id):
        pass

    def put(self, paste_id):
        pass

paste_api = PasteAPI.as_view('paste_api')
app.add_url_rule('/api/paste/<paste_id>', view_func=paste_api,
                 methods=['GET'])
app.add_url_rule('/api/paste/', view_func=paste_api, methods=['POST'])
