"""
The flask application package.
"""

from flask import Flask
from views.home import home
from views.api import api

app = Flask(__name__)
app.register_blueprint(home)
app.register_blueprint(api,url_prefix='/api')