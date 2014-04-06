from flask import render_template, redirect, url_for, abort, g
from flask.ext.login import (login_user, login_required, current_user, UserMixin,
                             logout_user)
from hashids import Hashids
from pygments import highlight
from pygments.lexers import get_lexer_by_name, ClassNotFound
from pygments.formatters import HtmlFormatter
from .app import app, db
from .forms import CreatePasteForm
from . import model


@app.before_request
def get_hashid():
    g.hashid = Hashids(salt=app.config['SECRET_KEY'], min_length=5)

@app.template_filter('encrypt')
def encrypt_filter(s):
    return g.hashid.encrypt(s)

@app.context_processor
def latest_pastes():
    pastes = model.Paste.query.order_by('created_on desc').limit(10).all()
    return dict(pastes=pastes)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CreatePasteForm()

    if form.validate_on_submit():
        paste = model.Paste(name=form.name.data,
                            content=form.content.data,
                            syntax=form.syntax.data)
        db.session.add(paste)
        db.session.commit()
        db.session.refresh(paste)
        
        paste_id = g.hashid.encrypt(paste.id)
        return redirect(url_for('show_paste', paste_id=paste_id))

    return render_template('index.html', form=form)

@app.route('/paste/<paste_id>')
def show_paste(paste_id):
    _id = g.hashid.decrypt(paste_id)
    paste = model.Paste.query.get(_id)
    if paste is None:
        abort(404)

    try:
        lexer = get_lexer_by_name(paste.syntax)
        formatter = HtmlFormatter(nobackground=True)
        output = highlight(paste.content, lexer, formatter)
    except ClassNotFound as ex:
        app.logger.error("Pygments error: %s" % str(ex))
        output = paste.content

    return render_template('show_paste.html', paste=paste, output=output)
