
from flask import request
from MyFlask.API.WeChatUtil.WeChat import WeChatServer

class TestClass(object):
    def reply_func(self,param_dict):
        param_dict['Content'] = 'hello,world'
        return param_dict

server = WeChatServer('demo')
server.register_callback('text',TestClass().reply_func)

