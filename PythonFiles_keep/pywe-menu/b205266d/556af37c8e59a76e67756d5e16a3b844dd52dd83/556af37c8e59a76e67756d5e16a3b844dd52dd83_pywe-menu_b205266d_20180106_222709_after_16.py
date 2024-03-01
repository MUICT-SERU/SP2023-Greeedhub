# -*- coding: utf-8 -*-

WECHAT = {
    'JSAPI': {
        'token': '5201314',
        'appID': 'appID',
        'appsecret': 'appsecret',
        'mchID': 'mchId',
        'apiKey': 'apiKey',
        'mch_cert': '/tmp/apiclient_cert.pem',
        'mch_key': '/tmp/apiclient_key.pem',
        'redpacket': {
            'SEND_NAME': u'SEND_NAME',
            'NICK_NAME': u'NICK_NAME',
            'ACT_NAME': u'ACT_NAME',
            'WISHING': u'WISHING！',
            'REMARK': u'REMARK',
        }
    }
}

OPENID = ''

MENUS = {
    'button': [
        {
            'type': 'click',
            'name': u'Pywe',
            'key': 'V1001_PYWE'
        }
    ]
}

CONDITIONALMENUS = {
    'button': [
        {
            'type': 'click',
            'name': u'Pywe',
            'key': 'V1001_PYWE'
        },
        {
            'type': 'click',
            'name': u'Menu',
            'key': 'V1001_MENU'
        }
    ],
    'matchrule': {
        'country': u'中国'
    }

}
