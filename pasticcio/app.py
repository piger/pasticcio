# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel


app = Flask('pasticcio')
db = SQLAlchemy(app)
babel = Babel(app)

app.config['SITE_TITLE'] = 'Pasticcio'
