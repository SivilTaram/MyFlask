from MyFlask.API.WeChatUtil.WeChat import WeChatServer
from flask import Blueprint

api = Blueprint('api',__name__)

class TestClass(object):
    def reply_func(self,param_dict):
        param_dict['Content'] = 'hello,world'
        return param_dict

server = WeChatServer(api,'demo')
server.register_callback('text', TestClass().reply_func)
