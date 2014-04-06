# -*- coding: utf-8 -*-
import os
import argparse
from hashids import Hashids
from .app import app, db
from .cleaner import cleaner

from . import model
from . import views
from . import api


def create_app(config=None):
    if config is not None:
        app.config.update(config)

    app.config.from_envvar('APP_CONFIG', silent=True)
    db.create_all()
    app.hashid = Hashids(salt=app.config['SECRET_KEY'])

    return app

def run_server(args):
    create_app().run()

def run_cleaner(args):
    create_app()
    cleaner(args)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="Specify a configuration file")

    subp = parser.add_subparsers()
    cmd_clean = subp.add_parser('cleaner', help="Delete expired pastes")
    cmd_clean.set_defaults(func=run_cleaner)

    cmd_server = subp.add_parser('server', help="Run development server")
    cmd_server.set_defaults(func=run_server)

    args = parser.parse_args()

    if not args.config and not 'APP_CONFIG' in os.environ:
        parser.error("You must specify a configuration file")
    else:
        os.environ['APP_CONFIG'] = os.path.abspath(args.config)

    args.func(args)
