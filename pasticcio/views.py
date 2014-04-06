from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, abort, g, request, flash
from flask.ext.login import (login_user, login_required, current_user, UserMixin,
                             logout_user)
from flask_babel import to_user_timezone, lazy_gettext as _
from hashids import Hashids
from pygments import highlight
from pygments.lexers import get_lexer_by_name, ClassNotFound
from pygments.formatters import HtmlFormatter
from .app import app, db
from . import forms
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

@app.before_request
def autoexpire():
    if not app.config.get('AUTOEXPIRE', False):
        return
    count = model.Paste.purge()
    if count:
        app.logger.debug("Auto-purged %d pastes" % count)

@app.template_filter('encrypt')
def encrypt_filter(s):
    return g.hashid.encrypt(s)

@app.context_processor
def latest_pastes():
    pastes = model.Paste.query.order_by('created_on desc').limit(10).all()
    return dict(latest_pastes=pastes)

@app.context_processor
def active_if_processor():
    def active_if(endpoint):
        if request.endpoint == endpoint:
            return 'active'
        return ''
    return dict(active_if=active_if)

@app.template_filter()
def timesince(dt, reverse=False):
    """Convert a timestamp to a textual string describing "how much time ago".

    The parameter `dt` is a :class:`datetime.datetime` instance without
    timezone info (e.g. `tzinfo=None`).

    Original author: Dan Jacob
    URL: http://flask.pocoo.org/snippets/33/
    License: Public Domain
    """

    default = _(u'now')

    user_dt = to_user_timezone(dt)
    now_dt = to_user_timezone(datetime.utcnow())

    if reverse:
        diff = user_dt - now_dt
    else:
        diff = now_dt - user_dt

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
            if reverse:
                return _("%(num)s %(time)s", num=period, time=timestr)
            else:
                return _("%(num)s %(time)s ago", num=period, time=timestr)

    return default

def decrypt_paste_id(paste_id):
    try:
        _id = g.hashid.decrypt(paste_id)[0]
        _id = int(_id)
    except (ValueError, TypeError, IndexError):
        return None
    return _id

@app.route('/', methods=['GET', 'POST'])
def index():
    form = forms.CreatePasteForm()

    if form.validate_on_submit():
        expire_on = model.Paste.get_expiration_date(form.expire_on.data)
        paste = model.Paste(name=form.name.data,
                            content=form.content.data,
                            syntax=form.syntax.data,
                            expire_on=expire_on,
                            user=g.user)
        db.session.add(paste)
        db.session.commit()
        db.session.refresh(paste)
        
        paste_id = g.hashid.encrypt(paste.id)
        return redirect(url_for('show_paste', paste_id=paste_id))

    return render_template('index.html', form=form)

@app.route('/paste/<paste_id>')
def show_paste(paste_id):
    _id = decrypt_paste_id(paste_id)
    if _id is None:
        abort(404)
    paste = model.Paste.query.get(_id)
    if paste is None:
        flash("Paste not found!", "warning")
        return redirect(url_for('index'))

    delete_form = forms.Form()

    try:
        lexer = get_lexer_by_name(paste.syntax)
        formatter = HtmlFormatter(linenos='table', anchorlinenos=True,
                                  lineanchors='line')
        output = highlight(paste.content, lexer, formatter)
    except ClassNotFound as ex:
        app.logger.error("Pygments error: %s" % str(ex))
        output = paste.content

    return render_template('show_paste.html', paste=paste, output=output,
                           delete_form=delete_form)

@app.route('/edit/<paste_id>', methods=['GET', 'POST'])
def edit_paste(paste_id):
    _id = decrypt_paste_id(paste_id)
    if _id is None:
        abort(404)
    paste = model.Paste.query.get(_id)
    if paste is None:
        flash("Paste not found!", "warning")
        return redirect(url_for('index'))

    if paste.user != g.user:
        abort(401)

    form = forms.CreatePasteForm(obj=paste)
    if form.validate_on_submit():
        expire_on = model.Paste.get_expiration_date(form.expire_on.data)
        paste.expire_on = expire_on
        paste.name = form.name.data
        paste.content = form.content.data
        paste.syntax = form.syntax.data
        db.session.commit()

        return redirect(url_for('show_paste', paste_id=paste_id))

    return render_template('edit_paste.html', form=form, paste=paste)

@app.route('/user/<user>')
def user_pastes(user):
    pastes = model.Paste.query.filter_by(user=user).\
             order_by('created_on desc')
    return render_template('user_pastes.html', pastes=pastes, user=user)

@app.route('/delete/<paste_id>', methods=['POST'])
def delete_paste(paste_id):
    _id = decrypt_paste_id(paste_id)
    if _id is None:
        abort(404)
    paste = model.Paste.query.get(_id)
    if paste is None:
        abort(404)

    if paste.user != g.user:
        abort(401)

    form = forms.Form()
    if form.validate_on_submit():
        title = paste.title
        db.session.delete(paste)
        db.session.commit()

        flash(u"Paste %s deleted" % title, "success")

        return redirect(url_for('index'))

    abort(400)
