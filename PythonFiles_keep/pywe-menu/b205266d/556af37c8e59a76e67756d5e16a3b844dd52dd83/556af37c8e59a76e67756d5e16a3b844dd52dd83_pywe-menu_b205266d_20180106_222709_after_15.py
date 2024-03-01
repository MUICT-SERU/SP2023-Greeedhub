# -*- coding: utf-8 -*-

from local_wecfg_example import CONDITIONALMENUS, MENUS, OPENID, WECHAT
from pywe_menu import (Menu, add_conditional, create_menu, del_conditional, del_menu, delete_conditional, delete_menu,
                       get_current_selfmenu_info, get_menu, try_match)


class TestMenuCommands(object):

    def test_create_nenu(self):
        """
        {u'errcode': 0, u'errmsg': u'ok'}
        {u'errcode': 40018, u'errmsg': u'invalid button name size hint: [2gMLZa0881vr29]'}
        {u'errcode': 40019, u'errmsg': u'invalid button key size hint: [pjPYTA0402vr32]'}
        {u'errcode': 44002, u'errmsg': u'empty post data hint: [pr1Z30406vr21]'}
        """
        appid = WECHAT.get('JSAPI', {}).get('appID')
        appsecret = WECHAT.get('JSAPI', {}).get('appsecret')

        menu = Menu(appid=appid, secret=appsecret)
        menu1 = menu.create_menu(MENUS)
        assert isinstance(menu1, dict)
        assert menu1['errcode'] == 0
        assert menu1['errmsg'] == 'ok'

        menu2 = create_menu(MENUS, appid=appid, secret=appsecret)
        assert isinstance(menu2, dict)
        assert menu2['errcode'] == 0
        assert menu2['errmsg'] == 'ok'

    def test_get_menu(self):
        """
        {u'errcode': 46003, u'errmsg': u'menu no exist hint: [P4hmBa0165vr21]'}
        """
        appid = WECHAT.get('JSAPI', {}).get('appID')
        appsecret = WECHAT.get('JSAPI', {}).get('appsecret')

        menu = Menu(appid=appid, secret=appsecret)
        menu.create_menu(MENUS)

        menus1 = menu.get_menu()
        assert isinstance(menus1, dict)

        menus2 = get_menu(appid=appid, secret=appsecret)
        assert isinstance(menus1, dict)

        assert menus1 == menus2

        # 不存在的菜单数据
        del_menu(appid=appid, secret=appsecret)
        menus3 = get_menu(appid=appid, secret=appsecret)
        assert menus3['errcode'] == 46003

    def test_del_menu(self):
        appid = WECHAT.get('JSAPI', {}).get('appID')
        appsecret = WECHAT.get('JSAPI', {}).get('appsecret')

        menu = Menu(appid=appid, secret=appsecret)
        menu1 = menu.delete_menu()
        assert isinstance(menu1, dict)
        assert menu1['errcode'] == 0
        assert menu1['errmsg'] == 'ok'

        menu2 = delete_menu(appid=appid, secret=appsecret)
        assert isinstance(menu2, dict)
        assert menu2['errcode'] == 0
        assert menu2['errmsg'] == 'ok'

    def test_add_conditional(self):
        """
        {u'errcode': 0, u'errmsg': u'ok'}
        {u'errcode': 65303, u'errmsg': u'there is no selfmenu, please create selfmenu first hint: [kufg3a0431vr21]'}
        {u'errcode': 65304, u'errmsg': u'match rule empty hint: [.9S05a0657vr23]'}
        """
        appid = WECHAT.get('JSAPI', {}).get('appID')
        appsecret = WECHAT.get('JSAPI', {}).get('appsecret')

        menu = Menu(appid=appid, secret=appsecret)

        # 没有默认菜单，不能创建个性化菜单
        menu0 = menu.try_match(OPENID)
        assert isinstance(menu0, dict)
        assert menu0['errcode'] == 65303

        # 创建自定义菜单
        menu.create_menu(MENUS)

        # MatchRule 信息为空
        menu1 = menu.add_conditional(MENUS)
        assert isinstance(menu1, dict)
        assert menu1['errcode'] == 65304

        menu2 = add_conditional(MENUS, appid=appid, secret=appsecret)
        assert isinstance(menu2, dict)
        assert menu2['errcode'] == 65304

        menu3 = menu.add_conditional(CONDITIONALMENUS)
        assert isinstance(menu3, dict)
        assert menu3['menuid']

        menu4 = add_conditional(CONDITIONALMENUS, appid=appid, secret=appsecret)
        assert isinstance(menu4, dict)
        assert menu4['menuid']

    def test_del_conditional(self):
        """
        {u'errcode': 0, u'errmsg': u'ok'}
        {u'errcode': 65301, u'errmsg': u'this menu is not conditionalmenu hint: [JkV3pa0141vr25]'}
        """
        appid = WECHAT.get('JSAPI', {}).get('appID')
        appsecret = WECHAT.get('JSAPI', {}).get('appsecret')

        menu = Menu(appid=appid, secret=appsecret)

        # 创建自定义菜单
        menu.create_menu(MENUS)

        # 不存在此 menuid 对应的个性化菜单
        menu0 = menu.delete_conditional('menuid')
        assert isinstance(menu0, dict)
        assert menu0['errcode'] == 65301

        menuid1 = menu.add_conditional(CONDITIONALMENUS)['menuid']
        menu1 = menu.del_conditional(menuid1)
        assert isinstance(menu1, dict)
        assert menu1['errcode'] == 0
        assert menu1['errmsg'] == 'ok'

        menuid2 = menu.add_conditional(CONDITIONALMENUS)['menuid']
        menu2 = del_conditional(menuid2, appid=appid, secret=appsecret)
        assert isinstance(menu2, dict)
        assert menu2['errcode'] == 0
        assert menu2['errmsg'] == 'ok'

    def test_try_match(self):
        """
        {u'errcode': 65303, u'errmsg': u'there is no selfmenu, please create selfmenu first hint: [kufg3a0431vr21]'}
        """
        appid = WECHAT.get('JSAPI', {}).get('appID')
        appsecret = WECHAT.get('JSAPI', {}).get('appsecret')

        menu = Menu(appid=appid, secret=appsecret)
        menu.delete_menu()

        # 没有默认菜单，不能创建个性化菜单
        menu0 = menu.try_match(OPENID)
        assert isinstance(menu0, dict)
        assert menu0['errcode'] == 65303

        # 创建自定义菜单
        menu.create_menu(MENUS)
        # 创建个性化菜单
        menu.add_conditional(MENUS)

        menus1 = menu.try_match(OPENID)
        assert isinstance(menus1, dict)

        menus2 = try_match(OPENID, appid=appid, secret=appsecret)
        assert isinstance(menus2, dict)

        assert menus1 == menus2

    def test_get_current_selfmenu_info(self):
        appid = WECHAT.get('JSAPI', {}).get('appID')
        appsecret = WECHAT.get('JSAPI', {}).get('appsecret')

        menu = Menu(appid=appid, secret=appsecret)
        menu.create_menu(MENUS)

        menus1 = menu.get_current_selfmenu_info()
        assert isinstance(menus1, dict)

        menus2 = get_current_selfmenu_info(appid=appid, secret=appsecret)
        assert isinstance(menus1, dict)

        assert menus1 == menus2
