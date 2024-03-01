# -*- coding: utf-8 -*-

import urllib

from pywe_base import BaseWechat


class Oauth(BaseWechat):
    def __init__(self):
        super(Oauth, self).__init__()
        # 网页授权获取用户基本信息, Refer: http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
        self.WECHAT_OAUTH2_AUTHORIZE = self.OPEN_DOMAIN + '/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope={scope}&state={state}#wechat_redirect'
        self.WECHAT_OAUTH2_ACCESS_TOKEN = self.API_DOMAIN + '/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code'
        self.WECHAT_OAUTH2_USERINFO = self.API_DOMAIN + '/sns/userinfo?access_token={access_token}&openid={openid}'

    def get_oauth_code_url(self, appid=None, redirect_uri=None, scope='snsapi_base', redirect_url=None):
        return self.WECHAT_OAUTH2_AUTHORIZE.format(
            appid=appid,
            redirect_uri=urllib.quote_plus(redirect_uri),
            scope=scope,
            state=urllib.quote_plus(redirect_url)
        )

    def get_access_info(self, appid=None, secret=None, code=None):
        return self.get(self.WECHAT_OAUTH2_ACCESS_TOKEN, appid=appid, secret=secret, code=code)

    def get_userinfo(self, access_token=None, openid=None):
        return self.get(self.WECHAT_OAUTH2_USERINFO, access_token=access_token, openid=openid)


oauth = Oauth()
get_oauth_code_url = oauth.get_oauth_code_url
get_access_info = oauth.get_access_info
get_userinfo = oauth.get_userinfo
