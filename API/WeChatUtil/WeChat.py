# -*- coding:utf-8 -*-

"""
微信企业号消息接口封装模块
封装了多媒体消息接口以及普通文本消息接口
"""
import os
import sys
import time
import copy
import json
import logging
import tempfile
import mimetypes

import flask
import requests

import MyFlask.API.WeChatUtil.CryptoUtil as utils

'''
企业号请求URL
'''
WEIXIN_URL = 'https://qyapi.weixin.qq.com'


class WeChatBase(object):
    """
    微信消息发送与接收类的公共基类
    负责进行日志的初始化工作等
    """
    logger_ok = False

    def __init__(self, appname, ini_name):
        """
        基类构造函数
        @param appname: 应用名称
        @param ini_name: 配置文件路径
        @return:
        """
        self.appname = appname
        if ini_name:
            self.config = utils.get_config(ini_name)
        else:
            self.config = utils.get_config()
        self.logger = logging.getLogger('easy_wechat')
        self.init_logger()

    def init_logger(self):
        """
        初始化日志模块相关参数
        @return: None
        """
        if WeChatBase.logger_ok:
            return
        self.logger.setLevel(logging.INFO)
        log_path = self.config.get('system', 'log_path')
        log_name = self.config.get('system', 'log_name')

        if not (os.path.exists(log_path) and os.path.isdir(log_path)):
            log_path = tempfile.gettempdir()

        if not log_name:
            log_name = 'easy_wechat.log'

        # 日志格式化
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 记录日志到文件
        log_handler = logging.FileHandler(os.path.join(log_path, log_name))
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)

        # 记录日志到stderr
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        # 注意日志模块只需要被初始化一次
        # 所以要在这里进行标记
        WeChatBase.logger_ok = True


class WeChatClient(WeChatBase):
    """
    消息发送类
    """

    def __init__(self, appname, ini_name=None):
        """
        构造函数
        @param appname: 应用名称, 需要与配置文件中section对应
        @return: WeChatClient对象实例
        """
        super(WeChatClient, self).__init__(appname, ini_name)
        self.CorpID = self.config.get(self.appname, 'corpid')
        self.Secret = self.config.get(self.appname, 'secret')
        self.AppID = self.config.get(self.appname, 'appid')

    @staticmethod
    def url_request(url, get=True, data=''):
        """
        请求指定的URL
        @param url: 字符串
        @param get: 是否使用GET方法
        @param data: 附加数据(POST)
        @return: 转换为dict的请求结果
        """
        try:
            if get:
                req = requests.get(url)
            else:
                req = requests.post(url, data)
        except Exception as e:
            # wrap exception message with more detail
            raise type(e)('unable to retrieve URL: %s with exception: %s', (url, e.message))
        else:
            try:
                res_dict = json.loads(req.content)
            except Exception as e:
                raise type(e)('invalid json content: %s with exception: %s',
                              (req.content, e.message))
        return res_dict

    def get_token(self):
        """
        获取发送消息时的验证token
        @return: token字符串
        """
        token_url = '%s/cgi-bin/gettoken?corpid=%s&corpsecret=%s' \
                    % (WEIXIN_URL, self.CorpID, self.Secret)
        res = self.url_request(token_url)
        return res['access_token']

    def upload_media(self, file_type, file_path):
        """
        上传临时媒体素材到微信服务器
        @param file_type: 文件类型
        @param file_path: 文件绝对路径
        @return: 服务器返回值dict
        """

        def make_err_return(err_msg):
            """
            一个简单的内部函数, 将错误信息包装并返回
            @param err_msg: 错误信息
            @return:
            """
            return {
                'errcode': -1,
                'errmsg': err_msg,
            }

        if file_type not in ('image', 'voice', 'video', 'file'):
            errmsg = 'Invalid media/message format'
            self.logger.error(errmsg)
            return make_err_return(errmsg)
        try:
            post_url = '%s/cgi-bin/media/upload?access_token=%s&type=%s' \
                       % (WEIXIN_URL, self.get_token(), file_type)
        except Exception as e:
            self.logger.error(e.message)
            return make_err_return(e.message)
        try:
            file_dir, file_name = os.path.split(file_path)
            files = {'file': (file_name, open(file_path, 'rb'),
                              mimetypes.guess_type(file_path, strict=False), {'Expires': '0'})}
            r = requests.post(post_url, files=files)
        except Exception as e:
            self.logger.error(e.message)
            return make_err_return(e.message)
        try:
            res_dict = json.loads(r.content)
        except Exception as e:
            raise type(e)('invalid json content: %s with exception: %s',
                          (r.content, e.message))
        return res_dict

    def send_media(self, media_type, media_content, touser,
                   toparty='', totag=''):
        """
        发送消息/视频/图片给指定的用户
        @param media_type: 消息类型
        @param media_content: 消息内容, 是一个dict, 包含具体的描述信息
        @param touser: 用户名, '|'分割
        @param toparty: 分组名, '|'分割
        @param totag: 标签名, '|'分割
        @return: 服务器返回值dict
        """
        if media_type not in ('text', 'image', 'voice', 'video', 'file'):
            errmsg = 'Invalid media/message format'
            self.logger.error(errmsg)
            return {
                'errcode': -1,
                'errmsg': errmsg,
            }
        try:
            send_url = '%s/cgi-bin/message/send?access_token=%s' \
                       % (WEIXIN_URL, self.get_token())
        except Exception as e:
            # since all error code definitions of wechat is unknown
            # we simply just return -1 as our error code
            self.logger.error(e.message)
            return {
                'errcode': -1,
                'errmsg': e.message,
            }
        message_data = {
            "touser": touser,
            "toparty": toparty,
            "totag": totag,
            "msgtype": media_type,
            "agentid": self.AppID,
            media_type: media_content,
            "safe": "0"
        }
        raw_data = json.dumps(message_data, ensure_ascii=False)
        try:
            res = self.url_request(send_url, False, raw_data.encode('utf-8'))
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            errmsg = 'failed when post json data: %s to wechat server with exception: %s' \
                     % (raw_data, e.message)
            self.logger.error(errmsg)
            return {
                'errcode': -1,
                'errmsg': errmsg,
            }
        if int(res['errcode']) == 0:
            self.logger.info('send message successful to %s' % touser)
        else:
            self.logger.error('send message failed with error: %s' % res['errmsg'])
        return res


class WeChatServer(WeChatBase):
    """
    消息接收类(server)
    """

    def __init__(self, appname, ini_name, flaskapp):
        """
        构造函数
        @param flaskapp: 已经实例化的flask应用
        @param appname: APP名称, 与配置文件中section对应
        @return: 构造的对象
        """
        super(WeChatServer, self).__init__(appname, ini_name)
        self.callback_funcs = {
            'text': None,
            'image': None,
            'voice': None,
            'video': None,
            'shortvideo': None,
            'location': None,
        }
        token = self.config.get(appname, 'token')
        aes_key = self.config.get(appname, 'encoding_aes_key')
        corp_id = self.config.get(appname, 'corpid')
        self.wxcpt = utils.WXBizMsgCrypt(token, aes_key, corp_id)
        # flaskapp为api blueprint
        self.app = flaskapp
        # 为微信添加路由规则
        self.app.add_url_rule('/' + self.config.get('system', 'route_name'),
                              None, self.callback, methods=['GET', 'POST'])

    def register_callback(self, msg_type, func):
        """
        注册收到某种类型消息后的回调函数
        @param msg_type: 消息类型
        @param func: 回调函数
        @return: None
        """
        if msg_type in self.callback_funcs:
            self.callback_funcs[msg_type] = func
        else:
            raise KeyError('Invalid media type.')

    def callback(self):
        """
        响应对/weixin请求的函数
        @return: 返回响应内容
        """
        method = flask.request.method
        if method == 'GET':
            return self.verify()
        elif method == 'POST':
            return self.do_reply()
        else:
            self.logger.error('unsupported method, return 405 method not allowed')
            # unknown method, return 405 method not allowed
            flask.abort(405)

    def verify(self):
        """
        验证接口可用性
        @return: 回显字符串
        """
        verify_msg_sig = flask.request.args.get('msg_signature', '')
        timestamp = flask.request.args.get('timestamp', '')
        nonce = flask.request.args.get('nonce', '')
        echo_str = flask.request.args.get('echostr', '')
        # do decoding and return
        ret, echo_str_res = self.wxcpt.VerifyURL(verify_msg_sig, timestamp, nonce, echo_str)
        if ret != 0:
            self.logger.error('verification failed with return value %d' % ret)
            # if verification failed, return 403 forbidden
            flask.abort(403)
        else:
            return echo_str_res

    def do_reply(self):
        """
        根据消息类型调用对应的回调函数进行回复
        @return: 回复的消息, 按照微信接口加密
        """
        req_msg_sig = flask.request.args.get('msg_signature', '')
        timestamp = flask.request.args.get('timestamp', '')
        nonce = flask.request.args.get('nonce', '')
        req_data = flask.request.data
        ret, xml_str = self.wxcpt.DecryptMsg(req_data, req_msg_sig, timestamp, nonce)
        if ret == 0:
            param_dict = utils.xml_to_dict(xml_str)
            msg_type = param_dict.get("MsgType", '')
            if msg_type in self.callback_funcs:
                callback_func = self.callback_funcs[msg_type]
                if callback_func:
                    # call the callback function and get return message (dict)
                    res_dict = callback_func(copy.deepcopy(param_dict))
                    default_params = {
                        'MsgType': param_dict['MsgType'],
                        'CreateTime': int(time.time())
                    }
                    for key, val in default_params.items():
                        if not res_dict.get(key, None):
                            res_dict[key] = val
                    res_dict['ToUserName'] = param_dict['FromUserName']
                    res_dict['FromUserName'] = param_dict['ToUserName']
                    xml_data = utils.dict_to_xml(res_dict)
                    # encrypted_data 是加密后的回复消息
                    ret_val, encrypted_data = \
                        self.wxcpt.EncryptMsg(xml_data, nonce, timestamp)
                    if ret_val == 0:
                        self.logger.info('replied \' %s \' to %s' %
                                         (res_dict['Content'],res_dict.get('ToUserName', 'null')))
                        return flask.Response(encrypted_data, mimetype='text/xml')
        # 如果没有正确走完这个流程, 就记录日志返回错误
        self.logger.error('request failed with request data: %r' % req_data)
        # if decryption failed or all other reasons, return 400 bad request code
        flask.abort(400)

    #def run(self, *args, **kwargs):
    #    """
    #    启动server循环
    #    @param args: 参数列表
    #    @param kwargs: 参数字典
    #    @return: None
    #    """
    #    self.app.run(*args, **kwargs)
