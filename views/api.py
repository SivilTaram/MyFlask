from MyFlask.API.WeChatUtil.WeChat import WeChatServer
from flask import Blueprint

api = Blueprint('api',__name__)

class TestClass(object):
    def reply_func(self,param_dict):
        print ('Receive Message %s',param_dict['Content'])
        if param_dict['Content'] == '你是个傻瓜':
            param_dict['Content'] = '2333'
        else:
            param_dict['Content'] = 'hello,world'
        return param_dict

server = WeChatServer('demo','config.ini',api)

server.register_callback('text', TestClass().reply_func)
