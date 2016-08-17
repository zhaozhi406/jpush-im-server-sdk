#-*- coding:utf-8 -*-
'''
author: zhaozhi
created: 2016-08-16
brief: a jiguang IM rest api wrapper
'''

import requests
import base64
import json

jpush_app_key = "c2f3adaeced410ee9cf8feca"
jpush_master_secret = "e8aaa4505b45fb7a97cf1408"

class JMessageResult(object):
    class ErrCode(object):
        '''
        JG_ERR: 极光错误
        EXCEPTION: 请求异常
        '''
        OK = 0
        JG_ERR = 1
        EXCEPTION = 2

    def __init__(self, err, msg, data=None, jg_err=None):
        self.err = err
        self.msg = msg
        self.data = data
        self.jg_err = jg_err

    def toJson(self):
        return json.dumps({
            "err": self.err,
            "msg": self.msg,
            "data": self.data,
            "jg_err": self.jg_err
        })

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.toJson()

class JMessage(object):
    REQ_HOST = "https://api.im.jpush.cn"
    #连接, 读取超时
    REQ_TIMEOUT = (10, 10)
    VERSION = 1

    _APIS = {
        #注册管理员
        "admins": "/v1/admins/",
        #发送消息
        "messages": "/v1/messages",
        #用户信息
        "users": "/v1/users/"
    }
    def __init__(self, app_key, master_secret):
        self.app_key = app_key
        self.master_secret = master_secret

    def _genAuthString(self):
        return base64.b64encode("%s:%s" % (self.app_key, self.master_secret))

    def _getCommonHttpHeaders(self):
        return {
            "Authorization": "Basic " + self._genAuthString(),
            "Content-Type": "Application/json"
        }

    def _commonRequest(self, rest_api, params={}, http_method="GET"):
        headers = {}
        headers.update(self._getCommonHttpHeaders())
        resp = None
        http_method = http_method.lower()
        ret = JMessageResult(JMessageResult.ErrCode.OK, "")
        try:
            req_url = self.REQ_HOST + rest_api
            method = getattr(requests, http_method)
            if http_method == 'get':
                resp = method(req_url, headers=headers, params=params, timeout=self.REQ_TIMEOUT)
            elif http_method in ('post', 'put'):
                resp = method(req_url, headers=headers, json=params, timeout=self.REQ_TIMEOUT)
            else:
                resp = method(req_url, headers=headers, timeout=self.REQ_TIMEOUT)
            if resp.status_code >= 200 and resp.status_code < 300:
                ret.data = "" if resp.text == "" else json.loads(resp.text)
            else:
                ret.err = JMessageResult.ErrCode.JG_ERR
                ret.msg = u"jiguang error:" + resp.reason
                err = "" if resp.text == "" else json.loads(resp.text)
                ret.jg_err = err["error"] if "error" in err else err
        except Exception, e:
            ret.err = JMessageResult.ErrCode.EXCEPTION
            ret.msg = "exception: " + str(e) + ", " + ret.msg
        return ret

    def registerAdmin(self, username, password):
        '''
        注册管理员
        :param username:
        :param password:
        :return:
        '''
        return self._commonRequest(self._APIS["admins"], params={"username":username, "password":password}, http_method="post")

    def getAdminsList(self, start, count):
        '''
        获取管理员列表
        :param start: 起始记录位置 从0开始
        :param count: 查询条数 最多支持500条
        :return:
        '''
        return self._commonRequest(self._APIS["admins"], params={"start":start, "count":count}, http_method="get")

    def sendMessage(self, target_type, target_id, from_type, from_id, from_name=None, target_name=None,  msg_type="text", text="", extras=None):
        '''
        发送消息
        :param target_type:
        :param target_id:
        :param from_type:
        :param from_id:
        :param from_name:
        :param target_name:
        :param msg_type:
        :param text:
        :param extras:
        :return:
        '''
        return self._commonRequest(self._APIS["messages"], params={
            "version": self.VERSION,
            "target_type": target_type,
            "target_id": target_id,
            "from_type": from_type,
            "from_id": from_id,
            "from_name": from_name,
            "target_name": target_name,
            "msg_type": msg_type,
            "msg_body": {"text": text, "extras": extras}
        }, http_method="post")

    def getUserInfo(self, username):
        '''
        获取用户信息
        :param username:
        :return:
        '''
        return self._commonRequest(self._APIS["users"] + username)

    def registerUsers(self, users):
        '''
        批量注册用户,一次批量注册最多支持500个用户
        :param users: a list of dict, [{"username":"xxx", "password":"xxx"}, ...]
        :return:
        '''
        return self._commonRequest(self._APIS["users"], params=users, http_method="post")

if __name__ == "__main__":

    jm = JMessage(jpush_app_key, jpush_master_secret)
    # 注册管理员
    # print jm.registerAdmin("admin", "admin")

    # 查看管理员列表
    # print jm.getAdminsList(0, 2)

    # 注册用户
    # users = [{"username":"user123", "password":"123456"}]
    # ret = jm.registerUsers(users=users)

    # 查看用户信息
    #print jm.getUserInfo("user123")

    #发送消息
    # print jm.sendMessage(target_type="single", target_id="user123", target_name=u"user123的名字", from_type="admin", from_id="admin", from_name=u"admin的名字", text=u"im消息")

