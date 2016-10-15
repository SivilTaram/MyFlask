import MyFlask.API
from flask import Blueprint

api = Blueprint('api',__name__)

@api.route('getmessage',methods=['GET'])
def sendMsg():
    server
