# -*- coding: utf-8 -*-
import os
from optparse import OptionParser
from hashids import Hashids
from .app import app, db

from . import model
from . import views


def create_app(config=None):
    if config is not None:
        app.config.update(config)

    app.config.from_envvar('APP_CONFIG', silent=True)
    db.create_all()
    app.hashid = Hashids(salt=app.config['SECRET_KEY'])

    return app

def main():
    parser = OptionParser()
    parser.add_option('-c', '--config')
    (opts, args) = parser.parse_args()

    if not opts.config and not 'APP_CONFIG' in os.environ:
        parser.error("You must specify a configuration file")
    else:
        os.environ['APP_CONFIG'] = os.path.abspath(opts.config)

    create_app().run()
