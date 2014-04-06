from flask import json, jsonify, abort, redirect, url_for, request, g
from flask.views import MethodView
from .model import Paste, User, APIKey
from .app import app, db
from .views import decrypt_paste_id


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
        user = self._get_user()
        data = request.json
        if data is None:
            abort(400)
        app.logger.debug("request.json = %r" % request.json)

        expire_on = Paste.get_expiration_date(data['expire_on'])
        paste = Paste(name=data['name'],
                      content=data['content'],
                      syntax=data['syntax'],
                      expire_on=expire_on,
                      user=user)
        db.session.add(paste)
        db.session.commit()
        db.session.refresh(paste)
        
        return jsonify(status='ok', paste=paste.to_dict()), 201

    def delete(self):
        pass

    def put(self, paste_id):
        pass

paste_api = PasteAPI.as_view('paste_api')
app.add_url_rule('/api/paste/<paste_id>', view_func=paste_api,
                 methods=['GET'])
app.add_url_rule('/api/paste/', view_func=paste_api, methods=['POST'])
