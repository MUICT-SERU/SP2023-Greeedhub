# -*- coding: utf-8 -*-

from pywe_token import BaseToken, final_access_token


class Menu(BaseToken):
    def __init__(self, appid=None, secret=None, token=None, storage=None):
        super(Menu, self).__init__(appid=appid, secret=secret, token=token, storage=storage)
        # 自定义菜单创建接口, Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141013
        self.WECHAT_MENU_CREATE = self.API_DOMAIN + '/cgi-bin/menu/create'
        # 自定义菜单查询接口, Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141014
        self.WECHAT_MENU_GET = self.API_DOMAIN + '/cgi-bin/menu/get?access_token={access_token}'
        # 自定义菜单删除接口, Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421141015
        self.WECHAT_MENU_DELETE = self.API_DOMAIN + '/cgi-bin/menu/delete?access_token={access_token}'
        # 个性化菜单, Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1455782296
        # 创建个性化菜单
        self.WECHAT_MENU_ADDCONDITIONAL = self.API_DOMAIN + '/cgi-bin/menu/addconditional'
        # 删除个性化菜单
        self.WECHAT_MENU_DELCONDITIONAL = self.API_DOMAIN + '/cgi-bin/menu/delconditional'
        # 测试个性化菜单匹配结果
        self.WECHAT_MENU_TRYMATCH = self.API_DOMAIN + '/cgi-bin/menu/trymatch'
        # 获取自定义菜单配置接口, Refer: https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1434698695
        self.WECHAT_GET_CURRENT_SELFMENU_INFO = self.API_DOMAIN + '/cgi-bin/get_current_selfmenu_info?access_token={access_token}'

    def create_menu(self, menus, appid=None, secret=None, token=None, storage=None):
        return self.post(
            self.WECHAT_MENU_CREATE,
            params={
                'access_token': final_access_token(self, appid=appid, secret=secret, token=token, storage=storage),
            },
            data=menus,
        )

    def get_menu(self, appid=None, secret=None, token=None, storage=None):
        return self.get(self.WECHAT_MENU_GET, access_token=final_access_token(self, appid=appid, secret=secret, token=token, storage=storage))

    def del_menu(self, appid=None, secret=None, token=None, storage=None):
        return self.get(self.WECHAT_MENU_DELETE, access_token=final_access_token(self, appid=appid, secret=secret, token=token, storage=storage))

    def delete_menu(self, appid=None, secret=None, token=None, storage=None):
        return self.del_menu(appid=appid, secret=secret, token=token, storage=storage)

    def add_conditional(self, menus, appid=None, secret=None, token=None, storage=None):
        return self.post(
            self.WECHAT_MENU_ADDCONDITIONAL,
            params={
                'access_token': final_access_token(self, appid=appid, secret=secret, token=token, storage=storage),
            },
            data=menus,
        )

    def del_conditional(self, menuid, appid=None, secret=None, token=None, storage=None):
        return self.post(
            self.WECHAT_MENU_DELCONDITIONAL,
            params={
                'access_token': final_access_token(self, appid=appid, secret=secret, token=token, storage=storage),
            },
            data={
                'menuid': menuid,
            },
        )

    def delete_conditional(self, menuid, appid=None, secret=None, token=None, storage=None):
        return self.del_conditional(menuid=menuid, appid=appid, secret=secret, token=token, storage=storage)

    def try_match(self, user_id, appid=None, secret=None, token=None, storage=None):
        return self.post(
            self.WECHAT_MENU_TRYMATCH,
            params={
                'access_token': final_access_token(self, appid=appid, secret=secret, token=token, storage=storage),
            },
            data={
                'user_id': user_id,
            },
        )

    def get_current_selfmenu_info(self, appid=None, secret=None, token=None, storage=None):
        return self.get(self.WECHAT_GET_CURRENT_SELFMENU_INFO, access_token=final_access_token(self, appid=appid, secret=secret, token=token, storage=storage))


menu = Menu()
create_menu = menu.create_menu
get_menu = menu.get_menu
del_menu = menu.del_menu
delete_menu = menu.delete_menu
add_conditional = menu.add_conditional
del_conditional = menu.del_conditional
delete_conditional = menu.delete_conditional
try_match = menu.try_match
get_current_selfmenu_info = menu.get_current_selfmenu_info
