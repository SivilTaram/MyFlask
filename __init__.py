"""
The flask application package.
"""

from flask import Flask
from MyFlask.views.home import home
from MyFlask.views.api import api

app = Flask(__name__)
app.register_blueprint(home)
app.register_blueprint(api,url_prefix='/api')