"""
扯线木偶界面自动化应用编程接口(Puppet UIAutomation API)
技术群：624585416
"""
__author__ = "睿瞳深邃(https://github.com/Raytone-D)"
__project__ = 'Puppet'
__version__ = "0.4.21c"
__license__ = 'MIT'

# coding: utf-8
import ctypes
from functools import reduce
import time
import pyperclip

MSG = {'WM_SETTEXT': 12,
       'WM_GETTEXT': 13,
       'WM_KEYDOWN': 256,
       'WM_KEYUP': 257,
       'WM_COMMAND': 273,
       'BM_CLICK': 245,
       'CB_GETCOUNT': 326,
       'CB_SETCURSEL': 334,
       'CBN_SELCHANGE': 1,
       'COPY_DATA': 57634}

INIT = {'买入': 161, '卖出': 162, '撤单': 163}

NODE = {'FRAME': (59648, 59649),
        'FORM': (59648, 59649, 1047, 200, 1047),
        'ACCOUNT': (59392, 0, 1711),
        'COMBO': (59392, 0, 2322),
        'BUY': (1032, 1033, 1034, '买入[B]', 1036, 1018),
        'SELL':(1032, 1033, 1034, '卖出[S]', 1036, 1038),
        'CANCEL': (3348, '查询代码', '撤单'),
        'ENTRUSTMENT': 168,
        '撤单': 163,
        '双向委托': 512,
        '新股申购': 554,
        '中签查询': 1070}

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
           '报表': 1047}

NEW = {'新股代码': 1032,
       '新股名称': 1036,
       '申购价格': 1033,
       '可申购数量': 1018,
       '申购数量': 1034,
       '申购': 1006}

RAFFLE = ['新股代码', '证券代码', '申购价格']# , '申购上限']

VKCODE = {'F1': 112,
          'F2': 113,
          'F3': 114,
          'F4': 115,
          'F5': 116,
          'F6': 117}

op = ctypes.windll.user32

def switch_combo(index, idCombo, hCombo):
    op.SendMessageW(hCombo, MSG['CB_SETCURSEL'], index, 0)
    op.SendMessageW(op.GetParent(hCombo), MSG['WM_COMMAND'], MSG['CBN_SELCHANGE']<<16|idCombo, hCombo)

def click_button(dialog, label):
    handle = op.FindWindowExW(dialog, 0, 0, label)
    id_btn = op.GetDlgCtrlID(handle)
    op.PostMessageW(dialog, MSG['WM_COMMAND'], id_btn, 0)

def fill_in(container, _id_item, _str):
    op.SendDlgItemMessageW(container, _id_item, MSG['WM_SETTEXT'], 0, _str)

def kill_popup(hDlg, name='是(&Y)'):
    for x in range(100):
        time.sleep(0.01)
        popup = op.GetLastActivePopup(hDlg)
        if popup != hDlg and op.IsWindowVisible(popup):
            yes = op.FindWindowExW(popup, 0, 0, name)
            idYes = op.GetDlgCtrlID(yes)
            op.PostMessageW(popup, MSG['WM_COMMAND'], idYes, 0)
            print('popup has killed.')
            break

class Puppet:
    """
    界面自动化操控包装类
    # 方法 # '委买': buy(), '委卖': sell(), '撤单': cancel(), '打新': raffle(),
    # 属性 # '帐号': account, '可用余额': balance, '持仓': position, '成交': deals, '可撤委托': cancelable, 
    #      # '新股': new, '中签': bingo, 
    """
    def __init__(self, main=None, title='网上股票交易系统5.0'):

        print('我正在热身，稍等一下...')
        self._main = main or op.FindWindowW(0, title)
        self.buff = ctypes.create_unicode_buffer(32)
        self.switch = lambda node: op.SendMessageW(self._main, MSG['WM_COMMAND'], node, 0)
        if self._main:
            self._container = {label: self._get_item(_id) for label, _id in INIT.items()}

        self._position, self._cancelable, self._entrustment = None, None, None

        self.switch(NODE['双向委托'])
        time.sleep(0.5)

        self.two_way = reduce(op.GetDlgItem, NODE['FRAME'], self._main)
        self.members = {k: op.GetDlgItem(self.two_way, v) for k, v in TWO_WAY.items()}
        self._position = reduce(op.GetDlgItem, NODE['FORM'], self._main)
        print('我准备好了，开干吧！人生巅峰在前面！') if self._main else print("没找到已登录的客户交易端，我先撤了！")
        # 获取登录账号
        self.account = reduce(op.GetDlgItem, NODE['ACCOUNT'], self._main)
        op.SendMessageW(self.account, MSG['WM_GETTEXT'], 32, self.buff)
        self.account = self.buff.value

        #self.combo = reduce(op.GetDlgItem, NODE['COMBO'], self._main)
        #self.count = op.SendMessageW(self.combo, MSG['CB_GETCOUNT'])

    def _get_item(self, _id, sec=0.5):
        self.switch(_id)
        time.sleep(sec)
        return reduce(op.GetDlgItem, NODE['FRAME'], self._main)

    def switch_tab(self, hCtrl, keyCode, param=0):   # 单击
        op.PostMessageW(hCtrl, MSG['WM_KEYDOWN'], keyCode, param)
        time.sleep(0.1)
        op.PostMessageW(hCtrl, MSG['WM_KEYUP'], keyCode, param)

    def copy_data(self, hCtrl, key=0):    # background mode
        "将CVirtualGridCtrl|Custom<n>的数据复制到剪贴板，默认取当前的表格"
        if key:
            self.switch_tab(self.two_way, key)    # 切换到持仓('W')、成交('E')、委托('R')

        start = time.time()
        print("正在等待实时数据返回，请稍候...")
        # 查到只有列表头的空白数据等3秒...orz
        for i in range(10):
            time.sleep(0.3)
            op.SendMessageW(hCtrl, MSG['WM_COMMAND'], MSG['COPY_DATA'], NODE['FORM'][-1])
            ret = pyperclip.paste().splitlines()
            if len(ret) > 1:
                break

        temp = (x.split('\t') for x in ret)
        header = next(temp)
        if '参考市值' in header:
            header.insert(header.index('参考市值'), '市值')
            header.remove('参考市值')
        print('IT TAKE {} SECONDS TO GET REAL-TIME DATA'.format(time.time() - start))
        return tuple(dict(zip(header, x)) for x in temp)

    def _wait(self, container, id_item):
        self.buff.value = ''  # False，待假成真
        for n in range(500):
            time.sleep(0.01)
            op.SendDlgItemMessageW(container, id_item, MSG['WM_GETTEXT'], 64, self.buff)
            if self.buff.value:
                break

    def _order(self, container, id_items, *triple):
        #self.switch(NODE['BUY'][0]
        fill_in(container, id_items[0], triple[0])  # 证券代码
        self._wait(container, id_items[-2])  # 证券名称
        fill_in(container, id_items[1], triple[1])  # 价格
        self._wait(container, id_items[-1])  # 可用数量
        fill_in(container, id_items[2], triple[2])  # 数量
        click_button(container, id_items[3])  # 下单按钮
        if len(str(triple[1]).split('.')[1]) == 3:  # 基金三位小数价格弹窗
            kill_popup(self._main)

    def buy(self, symbol, price, qty):
        self._order(self._container['买入'], NODE['BUY'], symbol, price, qty)

    def sell(self, symbol, price, qty):
        #self.switch(NODE['SELL'][0])
        self._order(self._container['卖出'], NODE['SELL'], symbol, price, qty)

    def buy2(self, symbol, price, qty, sec=0.3):   # 买入(B)
        #self.switch(NODE['双向委托'])
        op.SendMessageW(self.members['买入代码'], MSG['WM_SETTEXT'], 0, str(symbol))
        time.sleep(0.1)
        op.SendMessageW(self.members['买入价格'], MSG['WM_SETTEXT'], 0, str(price))
        time.sleep(0.1)
        op.SendMessageW(self.members['买入数量'], MSG['WM_SETTEXT'], 0, str(qty))
        #op.SendMessageW(self.members['买入'], MSG['BM_CLICK'], 0, 0)
        time.sleep(sec)
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], TWO_WAY['买入'], 0)
    
    def sell2(self, symbol, price, qty, sec=0.3):    # 卖出(S)
        #self.switch(NODE['双向委托'])
        op.SendMessageW(self.members['卖出代码'], MSG['WM_SETTEXT'], 0, str(symbol))
        time.sleep(0.1)
        op.SendMessageW(self.members['卖出价格'], MSG['WM_SETTEXT'], 0, str(price))
        time.sleep(0.1)
        op.SendMessageW(self.members['卖出数量'], MSG['WM_SETTEXT'], 0, str(qty))
        #op.SendMessageW(self.members['卖出'], MSG['BM_CLICK'], 0, 0)
        time.sleep(sec)
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], TWO_WAY['卖出'], 0)

    def refresh(self):    # 刷新(F5)
        op.PostMessageW(self.two_way, MSG['WM_COMMAND'], TWO_WAY['刷新'], 0)

    def cancel(self, symbol=None, choice='buy'):
        # 撤销指定代码的买单或者卖单。symbol必须是有效的证券代码。按代码撤单只在备注栏是“已报”状态才有效！
        fill_in(self._container['撤单'], NODE['CANCEL'][0], symbol)  # 填写代码
        click_button(self._container['撤单'], NODE['CANCEL'][1])  # 查询代码
        # 这里用撤单按钮的状态判断是否下一步
        self.cancel_sell() if choice == 'sell' else self.cancel_buy()
        ret = self.entrustment
        return [pair for pair in ret if '已撤' in pair['备注']] if ret else ret

    @property
    def balance(self):
        print('可用余额: %s' % ('$'*8))
        op.SendMessageW(self.members['可用余额'], MSG['WM_GETTEXT'], 32, self.buff)
        return self.buff.value

    @property
    def position(self):
        self.switch(NODE['双向委托'])
        return self.copy_data(self._position, ord('W'))

    @property
    def market_value(self):
        ret = self.position
        return sum((float(pair['市值']) for pair in ret)) if ret else ret

    @property
    def deals(self):
        print('当天成交: %s' % ('$'*8))
        return self.copy_data(self._position, ord('E'))
    
    @property
    def entrustment(self):
        if not self._entrustment:
            self.switch(NODE['ENTRUSTMENT'])
            self._entrustment = reduce(op.GetDlgItem, NODE['FORM'], self._main)

        return self.copy_data(self._entrustment)

    @property
    def cancelable(self):
        print('可撤委托: %s' % ('$'*8))
        ret = self.entrustment
        return [pair for pair in ret if '已报' in pair['备注']] if ret else ret

    @property
    def new(self):
        self.switch(NODE['新股申购'])
        time.sleep(0.5)
        self._new = reduce(op.GetDlgItem, NODE['FORM'], self._main)
        return self.copy_data(self._new)

    @property
    def bingo(self):
        self.switch(NODE['中签查询'])
        time.sleep(0.5)
        self._bingo = reduce(op.GetDlgItem, NODE['FORM'], self._main)
        return self.copy_data(self._bingo)

    def cancel_all(self):    # 全撤(Z)  # 只有撤单窗的按钮才能做到无弹窗撤单
        click_button(self._container['撤单'], '全撤(Z /)')

    def cancel_buy(self):    # 撤买(X)
        click_button(self._container['撤单'], '撤买(X)')

    def cancel_sell(self):    # 撤卖(C)
        click_button(self._container['撤单'], '撤卖(C)')

    def raffle(self, skip=False):    # 打新
        #op.SendMessageW(self._main, MSG['WM_COMMAND'], NODE['新股申购'], 0)
        #self._raffle = reduce(op.GetDlgItem, NODE['FORM'], self._main)
        #close_pop()    # 弹窗无需关闭，不影响交易。
        #schedule = self.copy_data(self._raffle)
        ret = self.new
        if not ret:
            print("是日无新!")
            return ret
        self._raffle = reduce(op.GetDlgItem, NODE['FRAME'], self._main)
        self._raffle_parts = {k: op.GetDlgItem(self._raffle, v) for k, v in NEW.items()}
            #new = [x.split() for x in schedule.splitlines()]
            #index = [new[0].index(x) for x in RAFFLE if x in new[0]]    # 索引映射：代码0, 价格1, 数量2
            #new = map(lambda x: [x[y] for y in index], new[1:])
        for new in ret:
            symbol, price = [new[y] for y in RAFFLE if y in new.keys()]
            if symbol[0] == '3' and skip:
                print("跳过创业板新股: {}".format(symbol))
                continue
            op.SendMessageW(self._raffle_parts['新股代码'], MSG['WM_SETTEXT'], 0, symbol)
            time.sleep(0.3)
            op.SendMessageW(self._raffle_parts['申购价格'], MSG['WM_SETTEXT'], 0, price)
            time.sleep(0.3)
            op.SendMessageW(self._raffle_parts['可申购数量'], MSG['WM_GETTEXT'], 32, self.buff)
            if not int(self.buff.value):
                print('跳过零数量新股：{}'.format(symbol))
                continue
            op.SendMessageW(self._raffle_parts['申购数量'], MSG['WM_SETTEXT'], 0, self.buff.value)
            time.sleep(0.3)
            op.PostMessageW(self._raffle, MSG['WM_COMMAND'], NEW['申购'], 0)

        #op.SendMessageW(self._main, MSG['WM_COMMAND'], NODE['双向委托'], 0)    # 切换到交易操作台
        return [new for new in self.cancelable if '配售申购' in new['操作']]

if __name__ == '__main__':
 
    trader = Puppet()
    #trader = Puppet(title='广发证券核新网上交易系统7.60')
    if trader.account:
        print(trader.account)           # 帐号
        print(trader.new)               # 查当天新股名单
        #trader.raffle()                # 打新，skip=True, 跳过创业板不打。
        #print(trader.balance)           # 可用余额
        #print(trader.position)          # 实时持仓
        #print(trader.deals)             # 当天成交
        #print(trader.cancelable)        # 可撤委托
        print(trader.market_value)
        print(trader.entrustment)        # 当日委托（可撤委托，已成委托，已撤销委托）
        #print(trader.bingo)             # 注意只兼容部分券商！
        #trader.cancel('002412')         # 默认choice='buy'，可选：'sell'
        #trader.cancel_all()
        #trader.cancel_buy()
        trader.cancel_sell()
        limit = '510160', '0.557', '100'
        trader.buy(*limit)
