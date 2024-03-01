"""
Puppet是一套以同花顺交易客户端为核心的完整的闭环实盘交易系统框架。
"""
__author__ = "睿瞳深邃(https://github.com/Raytone-D"
__project__ = 'Puppet'
__version__ = "0.4.3"

# coding: utf-8

import ctypes
from functools import reduce
import time
import pyperclip

CONSOLE = 59648, 59649

GRID = 1047, 200, 1047

ACCOUNT = 59392, 0, 1711

NODE = {'买入': 161,
        '卖出': 162,
        '撤单': 163,
        '双向委托': 512,
        '新股申购': 554}

TWO_WAY = {'买入代码': 1032,
           '买入价格': 1033,
           '买入数量': 1034,
           '买入': 1006,
           '卖出代码': 1035,
           '卖出价格': 1058,
           '卖出数量': 1039,
           '卖出': 1008,
           '可用余额': 1038,
           '刷新': 32790,
           '全撤': 30001,
           '撤买': 30002,
           '撤卖': 30003,
           '报表': 1047}

TAB = {'持仓': ord('W'),
       '成交': ord('E'),
       '委托': ord('R')}

SCHEDULE = {'证券代码': '',
            '证券名称': '',
            '实际数量': '',
            '市值': ''}

CANCEL = {'全选': 1098,
          '撤单': 1099,
          '全撤': 30001,
          '撤买': 30002,
          '撤卖': 30003,
          '空白': 3348,
          '查单': 3349}

NEW = {'新股代码': 1032,
       '新股名称': 1036,
       '申购价格': 1033,
       '可申购数量': 1018,
       '申购数量': 1034,
       '申购': 1006}

MSG = {'WM_SETTEXT': 12,
       'WM_GETTEXT': 13,
       'WM_KEYDOWN': 256,
       'WM_KEYUP': 257,
       'WM_COMMAND': 273}

CMD = {'COPY': 57634}

VKCODE = {'F1': 112,
          'F2': 113,
          'F3': 114,
          'F4': 115,
          'F5': 116,
          'F6': 117}

MKT = {'CYB': '3',
       'SH': '7',
       'SZ': '0',
       '创业板': '3',
       '沪市': '7',
       '深市': '0'}

op = ctypes.windll.user32

class Puppet():
    """
    # 方法 # '委买': buy(), '委卖': sell(), '撤单': cancel(), '打新': raffle()
    # 属性 # '可用余额': balance, '持仓': position, '成交': deals, '可撤委托': cancelable
    """
    def __init__(self, main=0):

        print('我正在热身，稍等一下...')
        self.main = main if main else op.FindWindowW(0, "网上股票交易系统5.0")
        op.SendMessageW(self.main, MSG['WM_COMMAND'], NODE['双向委托'], 0)    # 切换到交易操作台
        self.wait_a_second = lambda sec=0.2: time.sleep(sec)
        self.wait_a_second()    # 可调整区间值(0.01~0.5)
        self.buff = ctypes.create_unicode_buffer(32)
        self.two_way = reduce(op.GetDlgItem, CONSOLE, self.main)
        self.members = {k: op.GetDlgItem(self.two_way, v) for k, v in TWO_WAY.items()}
        print('我准备好了，开干吧！人生巅峰在前面！') if self.main else print("没找到已登录的客户交易端，我先撤了！")
        # 获取登录账号
        self.account = reduce(op.GetDlgItem, ACCOUNT, self.main)
        op.SendMessageW(self.account, MSG['WM_GETTEXT'], 32, self.buff)
        self.account = self.buff.value

    def switch_tab(self, hCtrl, keyCode, param=0):   # 单击
        op.PostMessageW(hCtrl, MSG['WM_KEYDOWN'], keyCode, param)
        self.wait_a_second(0.5)
        op.PostMessageW(hCtrl, MSG['WM_KEYUP'], keyCode, param)

    def copy_data(self, key=0):    # background mode
        "将CVirtualGridCtrl|Custom<n>的数据复制到剪贴板，默认取当前的表格"
        if key:
            self.switch_tab(self.two_way, key)    # 切换到持仓('W')、成交('E')、委托('R')
        print("正在等待实时数据返回，请稍候...")
        self.wait_a_second(1)    # 等待数据返回的秒数自行调整，一般sec>=1
        op.SendMessageW(reduce(op.GetDlgItem, CONSOLE+GRID, self.main),
                        MSG['WM_COMMAND'], CMD['COPY'], GRID[-1])

        return pyperclip.paste()

    def buy(self, symbol, price, qty):   # 买入(B)
        op.SendMessageW(self.members['买入代码'], MSG['WM_SETTEXT'], 0, symbol)
        op.SendMessageW(self.members['买入价格'], MSG['WM_SETTEXT'], 0, price)
        op.SendMessageW(self.members['买入数量'], MSG['WM_SETTEXT'], 0, qty)
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], TWO_WAY['买入'], self.members['买入'])

    def sell(self, symbol, price, qty):    # 卖出(S)
        op.SendMessageW(self.members['卖出代码'], MSG['WM_SETTEXT'], 0, symbol)
        op.SendMessageW(self.members['卖出价格'], MSG['WM_SETTEXT'], 0, price)
        op.SendMessageW(self.members['卖出数量'], MSG['WM_SETTEXT'], 0, qty)
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], TWO_WAY['卖出'], self.members['卖出'])

    def refresh(self):    # 刷新(F5)
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], TWO_WAY['刷新'], self.members['刷新'])

    def cancel(self, way=CANCEL['撤买'], symbol='000000'):

        op.SendMessageW(self.main, MSG['WM_COMMAND'], NODE['撤单'], 0)    # 切换到撤单操作台
        if way != CANCEL['查单'] and symbol != '000000' and symbol.isdecimal():
            print(self.copy_data())
            self.cancel_c = reduce(op.GetDlgItem, CONSOLE, self.main)
            self.cancel_ctrl = {v: op.GetDlgItem(self.cancel_c, v) for k, v in CANCEL.items()}
            op.SendMessageW(self.cancel_ctrl['填单'], MSG['WM_SETTEXT'], 0, symbol)
            self.wait_a_second()
            op.PostMessageW(self.cancel_c, MSG['WM_COMMAND'], CANCEL['查单'], self.cancel_ctrl['查单'])
            op.PostMessageW(self.cancel_c, MSG['WM_COMMAND'], way, self.cancel_ctrl[way])
        schedule = self.copy_data()
        op.SendMessageW(self.main, MSG['WM_COMMAND'], NODE['双向委托'], 0)    # 必须返回交易操作台
        return schedule

    @property
    def balance(self):
        print('可用余额: %s' % ('$'*68))
        op.SendMessageW(self.members['可用余额'], MSG['WM_GETTEXT'], 32, self.buff)
        return self.buff.value

    @property
    def position(self):
        print('实时持仓: %s' % ('$'*68))
        return self.copy_data(TAB['持仓'])

    @property
    def deals(self):
        print('当天成交: %s' % ('$'*68))
        return self.copy_data(TAB['成交'])

    @property
    def cancelable(self):
        print('可撤委托: %s' % ('$'*68))
        return self.cancel(way=CANCEL['查单'])

    @property
    def new(self):
        print('新股名单: %s' % ('$'*68))
        return self.raffle(way=False)

    def cancel_all(self):    # 全撤(Z)
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], 30001, self.members[30001])

    def cancel_buy(self):    # 撤买(X)
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], 30002, self.members[30002])

    def cancel_sell(self):    # 撤卖(C)
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], 30003, self.members[30003])

    def cancel_last(self):    # 撤最后一笔，仅限华泰定制版有效
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], 2053, self.members[2053])

    def cancel_same(self):    # 撤相同代码，仅限华泰定制版
        #op.PostMessageW(self.two_way, WM_COMMAND, 30022, self.members[30022])
        pass

    def raffle(self, skip='', way=True):    # 打新股。
        op.SendMessageW(self.main, MSG['WM_COMMAND'], NODE['新股申购'], 0)
        #close_pop()    # 弹窗无需关闭，不影响交易。
        schedule = self.copy_data()
        if way:
            print("开始打新股%s" % ('>'*68))
            print(schedule)
            self.raffle_c = reduce(op.GetDlgItem, CONSOLE, self.main)
            self.raffle_ctrl = {k: op.GetDlgItem(self.raffle_c, v) for k, v in NEW.items()}
            new = tuple(line.split()[1] for line in schedule.splitlines()[1:])
            for symbol in new:
                op.SendMessageW(self.raffle_ctrl['新股代码'], MSG['WM_SETTEXT'], 0, symbol)
                self.wait_a_second(0.5)
                op.SendMessageW(self.raffle_ctrl['可申购数量'], MSG['WM_GETTEXT'], 32, self.buff)
                qty = self.buff.value
                if symbol[0].startswith(skip):
                    print({symbol: (qty, "跳过<%s>开头的新股！" % skip)})
                    continue
                if qty == '0':
                    print({symbol: (qty, "数量为零")})
                    continue
                op.SendMessageW(self.raffle_ctrl['申购数量'], MSG['WM_SETTEXT'], 0, qty)
                self.wait_a_second()
                op.PostMessageW(self.raffle_c, MSG['WM_COMMAND'], NEW['申购'], self.raffle_ctrl['申购'])
                print({symbol: (qty, "已申购")})
        op.SendMessageW(self.main, MSG['WM_COMMAND'], NODE['双向委托'], 0)    # 切换到交易操作台
        return schedule

if __name__ == '__main__':
 
    trader = Puppet()
    if trader.account:
        print(trader.account)           # 帐号
        print(trader.new)               # 查当天新股名单
        trader.raffle(MKT['创业板'])    # 确定打新股，跳过创业板不打。
        print(trader.balance)           # 可用余额
        print(trader.position)          # 实时持仓
        print(trader.deals)             # 当天成交
        print(trader.cancelable)        # 可撤委托
