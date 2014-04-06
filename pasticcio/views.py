from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, abort, g, request
from flask.ext.login import (login_user, login_required, current_user, UserMixin,
                             logout_user)
from flask_babel import to_user_timezone, lazy_gettext as _
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

@app.before_request
def get_user():
    user = request.environ.get('REMOTE_USER', 'sand')
    if user is None:
        abort(401)
    g.user = user

@app.template_filter('encrypt')
def encrypt_filter(s):
    return g.hashid.encrypt(s)

@app.context_processor
def latest_pastes():
    pastes = model.Paste.query.order_by('created_on desc').limit(10).all()
    return dict(pastes=pastes)

@app.template_filter()
def timesince(dt, default=None):
    """Convert a timestamp to a textual string describing "how much time ago".

    The parameter `dt` is a :class:`datetime.datetime` instance without
    timezone info (e.g. `tzinfo=None`).

    Original author: Dan Jacob
    URL: http://flask.pocoo.org/snippets/33/
    License: Public Domain
    """

    if default is None:
        default = _(u'now')

    user_dt = to_user_timezone(dt)
    now_dt = to_user_timezone(datetime.utcnow())

    diff = user_dt - now_dt

    periods = (
        (diff.days / 365, _(u'year'), _(u'years')),
        (diff.days / 30, _(u'month'), _(u'months')),
        (diff.days / 7, _(u'week'), _(u'weeks')),
        (diff.days, _(u'day'), _(u'days')),
        (diff.seconds / 3600, _(u'hour'), _(u'hours')),
        (diff.seconds / 60, _(u'minute'), _(u'minutes')),
        (diff.seconds, _(u'second'), _(u'seconds')),
    )

    for period, singular, plural in periods:
        if period:
            if period == 1:
                timestr = singular
            else:
                timestr = plural
            return _("%(num)s %(time)s", num=period, time=timestr)

    return default

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CreatePasteForm()

    if form.validate_on_submit():
        expires = {
            '1hr': timedelta(hours=1),
            '1d': timedelta(days=1),
            '1w': timedelta(weeks=1),
            '1M': timedelta(days=30),
        }
        expire_on = expires.get(form.expire_on.data)
        paste = model.Paste(name=form.name.data,
                            content=form.content.data,
                            syntax=form.syntax.data,
                            expire_on=datetime.utcnow() + expire_on,
                            user=g.user)
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
