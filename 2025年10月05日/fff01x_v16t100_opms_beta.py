import logging
import os
import smtplib
import time
from datetime import timedelta
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr

import MetaTrader5
import colorama
import pandas
import schedule


class C1Help:
    def __init__(self, symbol):
        """ 辅助类1/3: 通用于程序和进程
        @param symbol: 进程标的
        """
        self.symbol = symbol

    def d0log(self, content, level="info"):
        """ 输出和保存日志
        @param content: 日志内容
        @param level: info(默认)/warning/error/critical依次提高
        """
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        txt = f"[{self.symbol}/%(asctime)s] %(message)s"
        date = "%Y.%m.%d/%H:%M:%S"
        dict_color = {"warning": colorama.Fore.GREEN,
                      "error": colorama.Fore.YELLOW,
                      "critical": colorama.Fore.RED}
        fmt = logging.Formatter(dict_color[level] + txt, date) if level in dict_color else \
            logging.Formatter(txt, date)

        os.makedirs(".\\log") if not os.path.exists(".\\log") else None
        handler_file = logging.FileHandler(f".\\log\\{self.symbol}.txt")
        handler_stream = logging.StreamHandler()
        handler_file.setFormatter(fmt)
        handler_stream.setFormatter(fmt)
        logger.addHandler(handler_file)
        logger.addHandler(handler_stream)

        logger.warning(content) if level == "warning" else (
            logger.error(content)) if level == "error" else (
            logger.critical(content)) if level == "critical" else (
            logger.info(content))
        logger.handlers.clear()

    @staticmethod
    def d0title(content, position, sub=False):
        """ 标题样式
        @param content: 标题名称
        @param position: up/内容上方, down/内容下方
        @param sub: 是否是子标题(默认否)
        @return: 完整的标题样式
        """
        character = "-" if sub else "~"
        character = character * 42
        position_up = f"↓{character}↓"
        position_down = f"↑{character}↑"
        title_ = f"{position_up}{content}{position_up}" if position == "up" else \
            f"{position_down}{content}{position_down}" if position == "down" else None
        return title_


class C2Help:
    def __init__(self, c1help, symbol, secs_short, secs_middle, secs_long, secs_super,
                 email_addr_from, email_addr_to, email_smtp_host, email_smtp_port, email_smtp_password):
        """ 辅助类2/3: 只适用于且全部适用于进程
        @param c1help: 实例化主类
        @param symbol: 进程标的
        @param secs_short: 等待时长_较短
        @param secs_middle: 等待时长_中等
        @param secs_long: 等待时长_较长
        @param secs_super: 等待时长_超长
        @param email_addr_from: 邮件发送人
        @param email_addr_to: 邮件收件人
        @param email_smtp_host: smtp地址
        @param email_smtp_port: smtp接口
        @param email_smtp_password: smtp密码
        """
        # %实例一赋%
        self.secs_short = secs_short
        self.secs_middle = secs_middle
        self.secs_long = secs_long
        self.secs_super = secs_super
        self.email_addr_from = email_addr_from
        self.email_addr_to = email_addr_to
        self.email_smtp_host = email_smtp_host
        self.email_smtp_port = email_smtp_port
        self.email_smtp_password = email_smtp_password
        # %实例二赋%
        self.log = c1help.d0log
        # %综合混赋%
        self.ploy_quit = C0Core(symbol).d0ploy_quit

    def d0time_secs(self, length, sleep=False):
        """ 等待时长
        @param length: short/较短, middle/中等, long/较长, super/超长
        @param sleep: 是否休眠(默认否)
        @return: length对应的时长(HH:MM:SS)
        """
        dict_secs = {"short": self.secs_short,
                     "middle": self.secs_middle,
                     "long": self.secs_long,
                     "super": self.secs_super}
        secs = dict_secs[length] if length in dict_secs else 0
        time.sleep(secs) if sleep else None
        secs = timedelta(seconds=secs)
        return secs

    def d0send_email(self, content):
        """ 向邮箱发送信息
        @param content: 信息内容
        """
        name_from = "发件人名称"
        name_to = "收件人名称"
        subject = content

        msg = MIMEText(content, 'html', 'utf-8')
        msg["From"] = formataddr((Header(name_from, 'utf-8').encode(), self.email_addr_from))
        msg['To'] = Header(name_to, 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        smtp = smtplib.SMTP_SSL(self.email_smtp_host, self.email_smtp_port)
        smtp.login(self.email_addr_from, self.email_smtp_password)
        smtp.sendmail(self.email_addr_from, self.email_addr_to, msg.as_string())
        smtp.quit()

    def d0remind_strong(self, content, exit_=False):
        """ 全方位的强烈提醒
        @param content: 提醒的内容
        @param exit_: 是否直接退出策略(默认否)
        """
        last_error = str(MetaTrader5.last_error())
        self.log(f"~强烈提醒~ 最后错误={last_error}", level="error") if not exit_ else None
        self.log(f"$强烈提醒$ 提醒内容={content}", level="critical")
        self.d0send_email(f"提醒内容={content}; 最后错误={last_error}")
        self.ploy_quit() if exit_ else None


# noinspection PyProtectedMember
class C0Into:
    def __init__(self, c1help, symbol, bar_frame):
        """ 从外部输入数据
        @param c1help: 实例化主类
        @param symbol: 进程标的
        @param bar_frame: 用于判断分析方向的K线周期
        """
        # &实例一赋&
        self.symbol = symbol
        self.bar_frame = bar_frame
        # &实例二赋&
        self.log = c1help.d0log

    def d0price_ask(self):
        """ 买入价格
        @return: /
        """
        ask = MetaTrader5.symbol_info_tick(self.symbol).ask
        return ask

    def d0price_bid(self):
        """ 卖出价格
        @return: /
        """
        bid = MetaTrader5.symbol_info_tick(self.symbol).bid
        return bid

    def d0tick_size(self):
        """ 每跳大小
        @return: /
        """
        size = MetaTrader5.symbol_info(self.symbol).point
        return size

    def d0tick_value(self):
        """ 每跳价值
        @return: /
        """
        value = MetaTrader5.symbol_info(self.symbol).trade_tick_value
        if self.symbol == "XAUUSD":  # mt5给出的XAUUSD的点值是0.1, 不知道为什么
            return 1
        else:
            return value

    def d0bar_source(self, bar_count):
        """ 数据源
        @param bar_count: K线数量
        @return: /
        """
        bar = MetaTrader5.copy_rates_from_pos(
            self.symbol, self.bar_frame, 0, bar_count)
        bar = pandas.DataFrame(bar)
        return bar

    def d0bar_format(self, bar_count):
        """ 格式化数据源
        @param bar_count: K线数量
        @return: df格式的格式化数据
        """
        bar = self.d0bar_source(bar_count)
        bar['time'] = pandas.to_datetime(bar['time'], unit='s')
        bar.index = bar['time']
        bar.index.name = 'date'
        bar = bar[['open', 'high', 'low', 'close']]
        bar = bar.sort_index()
        return bar

    def d0indicator_ma(self, bar_count):
        """ ma指标
        @param bar_count: 分析ma的K线的数量
        @return: ma
        """
        ma = self.d0bar_format(bar_count + 1).close.rolling(bar_count).mean()[-1]
        return ma

    def d0indicator_atr(self):
        """ atr指标
        @return: atr
        """
        bar = self.d0bar_format(300)
        for i in range(0, len(bar)):
            a = bar['high'][i] - bar['low'][i]
            b = abs(bar['close'][i - 1] - bar['high'][i])
            c = abs(bar['close'][i - 1]) - bar['low'][i]
            bar.loc[bar.index[i], 'TR'] = max(a, b, c)
        atr = bar['TR'].rolling(300).mean()[-1]
        return atr

    @staticmethod
    def d0id_valid(id_):
        """ 判断id是否依然有效(仍然持有仓位)
        @param id_: 需要判断的id
        @return: True/有效, False/无效
        """
        if MetaTrader5.positions_get(ticket=id_):
            return True
        else:
            return False

    def d0order_hold(self):
        """ 持单数据
        @return: df格式的持单数据(只能使用if xxx is not None/if xxx is None来判断返回值是否存在, 不能使用if xxx/if not xxx)
        """
        try:
            hold = MetaTrader5.positions_get(symbol=self.symbol)
            hold = pandas.DataFrame(list(hold), columns=hold[0]._asdict().keys())
            hold['time'] = pandas.to_datetime(hold['time'], unit='s')
            hold = hold[['ticket', 'time', 'type', 'volume', 'price_open', 'sl', 'tp', 'profit', 'symbol']]
            return hold
        except IndexError:
            return

    def d0order_pend(self):
        """ 挂单数据
        @return: df格式的挂单数据(只能使用if xxx is not None/if xxx is None来判断返回值是否存在, 不能使用if xxx/if not xxx)
        """
        try:
            pend = MetaTrader5.orders_get(symbol=self.symbol)
            pend = pandas.DataFrame(list(pend), columns=pend[0]._asdict().keys())
            pend['time_setup'] = pandas.to_datetime(pend['time_setup'], unit='s')
            pend = pend[['ticket', 'time_setup', 'type', 'volume_current', 'price_open', 'symbol']]
            return pend
        except IndexError:
            return

    def d0account_info(self):
        """ 账户信息
        @return: df格式的账户信息
        """
        try:
            account = MetaTrader5.account_info()._asdict()
            account = pandas.DataFrame(list(account.items()), columns=['property', 'value'])
            account.index = account['property']
            account = account[['value']]
            account = account.loc[['login', 'balance', 'profit', 'equity', 'margin', 'margin_free', 'margin_level']]
            return account
        except IndexError:
            self.log("$账户信息$ 分析失败: 类型错误", level="error")


class C0Away:
    def __init__(self, c1help, c2help, c0into, symbol, decimal, fail_max):
        """ 向外部输出数据
        注意: 所有指令均只执行发出而不判定执行结果. 如果需要的话, 可能需要进行人工确认
        @param c1help: 实例化主类
        @param c2help: 实例化主类
        @param c0into: 实例化主类
        @param symbol: 进程标的
        @param decimal: 通用小数
        @param fail_max: 发送订单的最高"连续"失败次数
        """
        # &实例一赋&
        self.symbol = symbol
        self.decimal = decimal
        self.fail_max = fail_max
        # &实例二赋&
        self.log = c1help.d0log
        self.time_secs = c2help.d0time_secs
        self.remind_strong = c2help.d0remind_strong
        self.order_hold = c0into.d0order_hold
        self.order_pend = c0into.d0order_pend
        # &综合直赋&
        self.new_count_fail = 0
        self.ploy_quit = C0Core(symbol).d0ploy_quit

    @staticmethod
    def d0type_buy():
        buy = MetaTrader5.ORDER_TYPE_BUY
        return buy

    @staticmethod
    def d0type_sell():
        sell = MetaTrader5.ORDER_TYPE_SELL
        return sell

    def d0send_order(self, type_, volume, price, sl, tp, deviation):
        """ 发送订单
        @param type_: 交易类型
        @param volume: 交易数量
        @param price: 交易价格
        @param sl: 自动止损
        @param tp: 自动止盈
        @param deviation: 最大的成交偏差(点)
        @return: fail/交易失败, 订单信息/订单id
        """
        request = {"action": MetaTrader5.TRADE_ACTION_DEAL,
                   "symbol": self.symbol,
                   "type": type_,
                   "volume": round(volume, 2),
                   "price": price,
                   "sl": float(sl),
                   "tp": float(tp),
                   "deviation": round(deviation),
                   "type_time": MetaTrader5.ORDER_TIME_GTC,
                   "type_filling": MetaTrader5.ORDER_FILLING_FOK}
        result = MetaTrader5.order_send(request)
        if result is None:
            self.remind_strong("$发送订单$ 发送失败: 返回空值, 可能是非交易时段或者策略有误", exit_=True)
        elif result.retcode != MetaTrader5.TRADE_RETCODE_DONE:
            self.d0send_statistics("fail")
            return "fail"
        else:
            self.d0send_statistics("success")
            deal_id = result.order
            deal_price = result.price
            return deal_id, deal_price

    def d0send_statistics(self, result):
        """ 统计发送订单的结果
        @param result: fail/失败, success/成功
        """
        if result == "fail":
            self.new_count_fail += 1
            if self.new_count_fail >= self.fail_max:
                self.remind_strong(f"$新建统计$ 新建订单连续失败{self.fail_max}次, "
                                   f"即将在{self.time_secs('super')}之后继续...")
                self.time_secs("super", sleep=True)
                self.new_count_fail = 0
        elif result == "success":
            self.new_count_fail = 0

    def d0modify_close(self, id_, price, type_="sl", first_sl=False):
        """ 修改止损/止盈
        @param id_: 订单ID
        @param price: 止损/止盈的价格
        @param type_: sl/止损(默认), tp/止盈
        @param first_sl: 是否是首次设置sl(默认否). 如果"是"但是修改失败, 则为了避免出现大亏的情况, 就必须先关闭订单
        """
        try:
            if type_ == "sl":
                request = {"action": MetaTrader5.TRADE_ACTION_SLTP, "position": id_, "sl": price}
            elif type_ == "tp":
                request = {"action": MetaTrader5.TRADE_ACTION_SLTP, "position": id_, "tp": price}
            else:
                request = None
            result = MetaTrader5.order_send(request)
            if result is None:
                self.remind_strong(f"$修改平仓$_{id_} 修改失败: 返回空值, 可能是非交易时段或者策略有误")
            elif result.retcode != MetaTrader5.TRADE_RETCODE_DONE:
                if first_sl:
                    self.remind_strong(f"$修改平仓$_{id_} 修改失败: 返回失败, 即将关闭订单以防止发生大亏",
                                       level="warning")
                    self.d0close_id(id_)
                else:
                    self.remind_strong(f"$修改平仓$_{id_} 修改失败: 返回失败, 即将保持订单但是放弃修改",
                                       level="warning")
        except TypeError:
            self.log(f"$修改平仓${id_} 修改失败: 类型错误", level="error")

    def d0close_id(self, id_):
        """ 根据单号关闭订单
        @param id_: 需要关闭订单的单号
        """
        try:
            MetaTrader5.Close(self.symbol, ticket=id_)
        except TypeError:
            self.log(f"$关闭单号$_{id_} 关闭失败: 类型错误", level="error")

    def d0clear_hold(self):
        """ 清空所有持单
        """
        if len(self.order_hold()) > 0:
            try:
                for i in self.order_hold()['ticket']:
                    MetaTrader5.Close(self.symbol, ticket=i)
            except TypeError:
                self.log("$清空持单$ 清空失败: 类型错误", level="error")

    def d0clear_pend(self):
        """ 清空所有挂单
        """
        if len(self.order_pend()) > 0:
            try:
                for i in self.order_pend()['ticket']:
                    request = {"order": i,
                               "action": MetaTrader5.TRADE_ACTION_REMOVE,
                               "type_time": MetaTrader5.ORDER_TIME_GTC,
                               "type_filling": MetaTrader5.ORDER_FILLING_IOC}
                    result = MetaTrader5.order_send(request)
                    if result.retcode != MetaTrader5.TRADE_RETCODE_DONE:
                        self.log(f"$清空挂单$ 清空失败: 单号={i}", level="warning")
            except TypeError:
                self.log("$清空挂单$ 清空失败: 类型错误", level="error")


class C3Help:
    def __init__(self, c1help, c2help, c0into, c0away, symbol, decimal,
                 balance_begin, balance_margin, balance_shrink):
        """ 辅助类3/3: 只适用于且部分适用于进程
        @param c1help: 实例化主类
        @param c2help: 实例化主类
        @param c0into: 实例化主类
        @param c0away: 实例化主类
        @param symbol: 进程标的
        @param decimal: 通用小鼠
        @param balance_begin: 初始资金
        @param balance_margin: 预付比例
        @param balance_shrink: 最大回撤
        """
        # %实例一赋%
        self.decimal = decimal
        self.balance_begin = balance_begin
        self.balance_margin = balance_margin
        self.balance_shrink = balance_shrink

        # %实例二赋%
        self.log = c1help.d0log
        self.time_secs = c2help.d0time_secs
        self.remind_strong = c2help.d0remind_strong
        self.order_hold = c0into.d0order_hold
        self.order_pend = c0into.d0order_pend
        self.account_info = c0into.d0account_info
        self.clear_hold = c0away.d0clear_hold
        self.clear_pend = c0away.d0clear_pend
        # &综合预赋&
        self.done_show_shrink = False
        self.done_show_margin = False
        # %综合混赋%
        self.config_connect = C0Core(symbol).d0config_connect
        self.ploy_quit = C0Core(symbol).d0ploy_quit

    def _arrange_holiday(self):
        """ 节假日/休息日的时间安排
        """
        content_end = "@事务处理@_假期收尾 正在进行假期休眠..."
        content_start = "$事务处理$_假期收尾 进入开盘并退出休眠"
        schedule.every().friday.at("23:59:00").do(self.log, content=content_end, level="warning")
        schedule.every().friday.at("23:59:00").do(time.sleep, 48 * 3600 + 2 * 60)
        schedule.every().monday.at("00:01:00").do(self.log, content=content_start, level="warning")
        schedule.run_pending()

    def _capital_shrink(self):
        """ 最大的回撤比例: 分析当前的账户回撤是否符合要求
        """
        balance = self.account_info().loc['balance', 'value']
        shrink = (self.balance_begin - balance) / self.balance_begin
        if shrink > 0:
            if shrink > self.balance_shrink:
                self.remind_strong(f"$事务处理$_最大回撤 "
                                   f"当前={round(shrink * 100, 2)}%>限制={self.balance_shrink * 100}%, "
                                   f"可能需要重新规划策略", exit_=True)
            elif shrink > self.balance_shrink * 0.8 and not self.done_show_shrink:
                self.remind_strong(f"$事务处理$_最大回撤 "
                                   f"当前={round(shrink * 100, 2)}%>限制={self.balance_shrink * 100}%の80%")
                self.done_show_shrink = True

    def _capital_margin(self):
        """ 最小的预付比例: 分析当前的预付款的比例是否符合要求
        """
        margin = self.account_info().loc['margin_level', 'value'] / 100
        if margin > 0:
            if margin < self.balance_margin:
                self.remind_strong(f"$事务处理$_最小预付 "
                                   f"当前={round(margin * 100, 2)}%<限制={self.balance_margin * 100}%. "
                                   f"即将自动清仓以释放预付款...")
                self._ensure_blank()
            elif margin < self.balance_margin * 1.2 and not self.done_show_margin:
                self.remind_strong(f"$事务处理$_最小预付 "
                                   f"当前={round(margin * 100, 2)}%<限制={self.balance_margin * 100}の120%")
                self.done_show_margin = True

    def _capital_balance(self):
        """ 期初时的资金复位: 在期初分析账户资金是否复位(每次启动程序都视为期初并显示且仅显示一次)
        """
        balance = round(self.account_info().loc['balance', 'value'])
        differ = abs(self.balance_begin - balance)
        percent = balance / self.balance_begin
        deal = "补充" if balance < self.balance_begin else "提取"
        self.log(f"$事务处理$_期初复位 "
                 f"结余/期初={balance}USD/{self.balance_begin}USD={round(percent * 100)}%, "
                 f"需要{deal}={differ}USD", level="warning")

    def _ensure_blank(self):
        """ 确保持单和挂单为空: 确保当前没有持单和挂单
        """
        self.clear_hold() if self.order_hold() is not None else None
        self.clear_pend() if self.order_pend() is not None else None

    def d0toolbox_common(self):
        """ 自定义组合_通用: 登录程序的时候需要处理的事项
        """
        self._capital_balance()

    def d0toolbox_ploy(self):
        """ 自定义组合_策略: 运行策略所需的环境
        """
        self.config_connect()
        self._arrange_holiday()
        self._capital_shrink()
        self._capital_margin()

    def d0toolbox_blank(self):
        """ 自定义组合_空仓: 确保当前没有持单和挂单
        """
        self._ensure_blank()


class C1Ploy:
    def __init__(self, c1help, c2help, c0into, c0away, c3help, symbol, decimal, bar_frame):
        """ 交易策略P1
        @param c1help: 实例化主类
        @param c2help: 实例化主类
        @param c0into: 实例化主类
        @param c0away: 实例化主类
        @param c3help: 实例化主类
        @param symbol: 通用标的
        @param decimal: 通用小数
        @param bar_frame: 操作周期
        """
        # &实例一赋&
        self.symbol = symbol
        self.decimal = decimal
        self.bar_frame = bar_frame
        # &实例二赋&
        self.log = c1help.d0log
        self.time_secs = c2help.d0time_secs
        self.remind_strong = c2help.d0remind_strong
        self.price_ask = c0into.d0price_ask
        self.price_bid = c0into.d0price_bid
        self.tick_size = c0into.d0tick_size
        self.tick_value = c0into.d0tick_value
        self.indicator_ma = c0into.d0indicator_ma
        self.indicator_atr = c0into.d0indicator_atr
        self.id_valid = c0into.d0id_valid
        self.order_hold = c0into.d0order_hold
        self.type_buy = c0away.d0type_buy
        self.type_sell = c0away.d0type_sell
        self.send_order = c0away.d0send_order
        self.modify_close = c0away.d0modify_close
        self.toolbox_ploy = c3help.d0toolbox_ploy
        self.toolbox_blank = c3help.d0toolbox_blank
        # &策略预赋&
        self.count_when_fast = 0
        self.count_when_slow = 0
        self.count_where_fast = 0
        self.count_where_slow = 0
        self.count_which_fast = 0
        self.count_which_slow = 0
        self.actual_sl_amount = 0
        self.when_fast = 0
        self.when_slow = 0
        self.where_fast = 0
        self.where_slow = 0
        self.which_fast = 0
        self.which_slow = 0
        self.open_id = 0
        self.open_price = 0
        self.open_volume = 0
        self.open_deviation = 0
        self.range_sl = 0
        self.range_cross_where = 0
        self.range_protect_touch = 0
        self.range_protect_move = 0
        self.limit_point_spread = 0
        self.open_type = "/"
        self.cross_where_old = ""
        self.cross_where_new = ""
        self.wait_buy = False
        self.wait_sell = False
        self.done_show = False
        self.done_open = False
        self.done_protect = False
        # &策略直赋&
        self.datum_sl_amount = 3  # TODO
        self.occupy_atr_sl = 2
        self.occupy_atr_cross_where = 0.1
        self.occupy_sl_protect_touch = 1
        self.occupy_sl_protect_move = 0.1
        self.occupy_sl_spread = 0.2
        self.common_point_spread = 30
        # &综合混赋&
        self.ploy_quit = C0Core(self.symbol).d0ploy_quit

    def d0circle_center(self):
        """ 统御所有分支函数以及其返回值的中心
        """
        if self.d0record_sync() is False:
            self.d0clear_data(always=True)
            self.log("~循环中心~ 即将开启新一轮的循环. 正在循环...")
        else:
            self.log("~循环中心~ 继续执行上一轮的循环. 正在循环...")
        while True:
            self.time_secs("short", sleep=True)
            self.toolbox_ploy()
            self.d0param_analyse()
            self.d0param_show()
            self.d0ma_cross()
            self.d0make_order() if self.d0common_limit() else None
            self.d0protect_cost()
            self.d0clear_data()
            self.d0record_deal(deal="write", content=f"{self.open_id} "
                                                     f"{self.open_price} "
                                                     f"'{self.open_type}' "
                                                     f"{self.done_open} "
                                                     f"{self.done_protect}")

    def d0record_sync(self):
        """ 每次启动程序的时候, 检查一下是否有上次程序退出之时未处理完成的订单数据
        @return: False/同步失败, 相关数据/同步成功
        """
        if self.d0record_deal() is False:
            return False
        else:
            try:
                open_id = self.d0record_deal()[0]
                if not self.id_valid(open_id):
                    self.log("$记录同步$ 同步失败: 单号为空/无效", level="warning")
                    return False
            except TypeError:
                self.log("$记录同步$ 同步失败: 类型错误", level="error")
                return False
            self.open_id = open_id
            self.open_price = self.d0record_deal()[1]
            self.open_type = self.d0record_deal()[2]
            self.done_open = self.d0record_deal()[3]
            self.done_protect = self.d0record_deal()[4]

    def d0record_deal(self, deal="read", content=None):
        """ 读取和写入数据到记录文件
        @param deal: write/写入, read/读取(默认)
        @param content: 写入内容(默认无)
        @return: False/处理失败, 相关数据/处理成功
        """
        os.makedirs(".\\record") if not os.path.exists(".\\record") else None
        file = f".\\record\\{self.symbol}.txt"
        if deal == "write":
            try:
                with open(file, 'w+') as f:
                    f.write(str(content))
            except TypeError:
                self.log("$记录处理$ 写入失败: 类型错误", level="error")
                return False
        elif deal == "read":
            try:
                list_data = []
                with open(file) as f:
                    for line in f:
                        list_data.extend([eval(i) for i in line.split()])
                    return list_data
            except FileNotFoundError:
                self.log("$记录处理$ 读取失败: 没有记录文件", level="warning")
                return False
            except SyntaxError:
                self.log("$记录处理$ 读取失败: 无效记录数据", level="warning")
                return False

    def d0param_analyse(self):
        """ 分析所有策略需要用到的参数
        """
        dict_test_param = {"AUDUSD": [],
                           "EURUSD": [2, 3, 21, 38, 110, 186, 3.22],
                           "GBPUSD": [2, 3, 27, 46, 115, 195, 3.12],
                           "NZDUSD": [],
                           "USDCAD": [],
                           "USDCHF": [],
                           "USDJPY": [2, 3, 20, 36, 119, 166, 3.46]}  # TODO
        list_test_param = dict_test_param[self.symbol]
        if self.symbol not in dict_test_param or list_test_param == []:
            self.log("$分析参数$ 分析失败: 尚未配置标的/标的参数为空", level="error")
            self.ploy_quit()
        else:
            self.count_when_fast = list_test_param[0]
            self.count_when_slow = list_test_param[1]
            self.count_where_fast = list_test_param[2]
            self.count_where_slow = list_test_param[3]
            self.count_which_fast = list_test_param[4]
            self.count_which_slow = list_test_param[5]
            self.actual_sl_amount = list_test_param[6]

        self.when_fast = self.indicator_ma(self.count_when_fast)
        self.when_slow = self.indicator_ma(self.count_when_slow)
        self.where_fast = self.indicator_ma(self.count_where_fast)
        self.where_slow = self.indicator_ma(self.count_where_slow)
        self.which_fast = self.indicator_ma(self.count_which_fast)
        self.which_slow = self.indicator_ma(self.count_which_slow)
        try:
            self.range_sl = self.indicator_atr() * self.occupy_atr_sl
            self.range_cross_where = self.indicator_atr() * self.occupy_atr_cross_where
            self.range_protect_touch = self.range_sl * self.occupy_sl_protect_touch
            self.range_protect_move = self.range_sl * self.occupy_sl_protect_move
            self.limit_point_spread = self.range_sl * self.occupy_sl_spread / self.tick_size()
            self.open_deviation = self.range_sl / self.tick_size() / 10
            self.open_volume = self.actual_sl_amount / (self.range_sl / self.tick_size() * self.tick_value())
        except ZeroDivisionError or AttributeError:
            self.log("$分析参数$ 分析失败: 可能是MT5暂时断连(必要时需人工排查)", level="error")

    def d0param_show(self):
        """ 是否显示参数信息
        """
        if not self.done_show:
            self.log(f"\n核心配置0: "
                     f"操作周期={self.bar_frame}(MT5代号)\n"
                     f"策略直赋0: "
                     f"标准止损={self.datum_sl_amount}USD, "
                     f"止损比例={self.occupy_atr_sl}*ATR, "
                     f"择位差幅={self.occupy_atr_cross_where}*ATR, "
                     f"触发平保={self.occupy_sl_protect_touch}*止损, "
                     f"移动平保={self.occupy_sl_protect_move}*止损, "
                     f"限制点差={self.occupy_sl_spread}*止损, "
                     f"通常点差={self.common_point_spread}点\n"
                     f"回测参数1: "
                     f"择时快线={self.count_when_fast}根, "
                     f"择时慢线={self.count_when_slow}根, "
                     f"择位快线={self.count_where_fast}根, "
                     f"择位慢线={self.count_where_slow}根, "
                     f"择向快线={self.count_which_fast}根, "
                     f"择向慢线={self.count_which_slow}根\n"
                     f"回测参数2: "
                     f"实际止损={self.actual_sl_amount}USD\n"
                     f"参数首示0: "
                     f"止损幅度={round(self.range_sl, self.decimal)}, "
                     f"择位差幅={round(self.range_cross_where, self.decimal)}, "
                     f"触发平保={round(self.range_protect_touch, self.decimal)}, "
                     f"移动平保={round(self.range_protect_move, self.decimal)}, "
                     f"点差极限={round(self.limit_point_spread)}点, "
                     f"开仓偏差={round(self.open_deviation)}点, "
                     f"开仓数量={round(self.open_volume, 2)}手")
            if self.common_point_spread >= self.limit_point_spread:
                self.log(f"通常点差={self.common_point_spread}>=点差极限={round(self.limit_point_spread)}, "
                         f"开仓频率可能不及预期(通过调整止损比例/操作周期/开仓金额等可以避免此类问题)", level="warning")
            self.done_show = True

    def d0common_limit(self):
        spread_ratio = (self.price_ask() - self.price_bid()) / self.range_sl
        result = True if spread_ratio <= self.occupy_sl_spread and self.open_volume > 0 else False
        if self.open_volume <= 0:
            self.log("$常规限制$ 开仓数量<=0(通过调整止损比例/操作周期/开仓金额等可以避免此类问题)", level="warning")
        return result

    def d0ma_cross(self):
        """ 分析MA的交叉情况
        """
        if self.where_fast > self.where_slow + self.range_cross_where:
            self.cross_where_old = self.cross_where_new
            self.cross_where_new = "long"
        elif self.where_fast < self.where_slow - self.range_cross_where:
            self.cross_where_old = self.cross_where_new
            self.cross_where_new = "short"
        if self.cross_where_old == "short" and self.cross_where_new == "long" and self.which_fast > self.which_slow:
            self.wait_buy = True
        elif self.cross_where_old == "long" and self.cross_where_new == "short" and self.which_fast < self.which_slow:
            self.wait_sell = True
        if self.wait_buy and self.when_fast > self.when_slow:
            self.open_type = "buy"
        elif self.wait_sell and self.when_fast < self.when_slow:
            self.open_type = "sell"

    def d0make_order(self):
        """ 判定是否可以制作订单
        """
        if self.order_hold() is None and not self.done_open and self.open_type != "/":
            basic = True if self.open_type == "buy" else False
            send = self.send_order(type_=self.type_buy() if basic else self.type_sell(),
                                   volume=self.open_volume,
                                   price=self.price_ask() if basic else self.price_bid(),
                                   sl=0,
                                   tp=0,
                                   deviation=self.open_deviation)
            if send != "fail":
                self.open_id = send[0]
                self.open_price = send[1]
                sl_price = self.open_price - self.range_sl if basic else self.open_price + self.range_sl
                self.modify_close(id_=self.open_id, price=sl_price, first_sl=True)
                self.done_open = True

    def d0protect_cost(self):
        """ 判定是否需要执行平保
        """
        if self.order_hold() is not None and not self.done_protect:
            if self.open_type == "buy" and self.price_bid() > self.open_price + self.range_protect_touch:
                self.modify_close(id_=self.open_id, price=self.open_price + self.range_protect_move)
                self.done_protect = True
            elif self.open_type == "sell" and self.price_ask() < self.open_price - self.range_protect_touch:
                self.modify_close(id_=self.open_id, price=self.open_price - self.range_protect_move)
                self.done_protect = True

    def d0clear_data(self, always=False):
        """ 判定是否清理数据
        盘中因为止损而导致单号无效无需判定, 因为没有大用
        @param always: 无论如何都始终清理(默认否)
        """
        if self.cross_where_new == "short":
            self.wait_buy = False
        elif self.cross_where_new == "long":
            self.wait_sell = False
        if (always or
                self.open_type == "buy" and self.cross_where_new == "short" or
                self.open_type == "sell" and self.cross_where_new == "long"):
            self.toolbox_blank()
            self.open_id = self.open_price = 0
            self.open_type = "/"
            self.done_open = self.done_protect = False


class C0Core:
    def __init__(self, symbol):
        """ 进行具体的统筹/赋值/实例化等的核心主类
        所有百分比都是以小数的形式来填写, 如果不是则需要在函数内部转换一下
        @param symbol: 进程标的
        """
        # 实参赋值
        self.symbol = symbol
        self.decimal = 5  # 默认小数位
        self.fail_max = 20  # 建立订单的最大失败次数
        self.bar_frame = MetaTrader5.TIMEFRAME_H1  # 操作周期 TODO
        self.balance_begin = 100  # 周期资金(USD), 与回测表格"完全"一致 TODO
        self.balance_shrink = 0.3  # 周期回撤(*100%), 与回测表格"近乎"2倍, 只能大不能小 TODO
        self.balance_margin = 2.0  # 保证金の最低比例(*100%) TODO
        self.secs_short = 10
        self.secs_middle = 1 * 60
        self.secs_long = 10 * 60
        self.secs_super = 30 * 60
        # 实例赋值
        self.c1help = None
        self.c2help = None
        self.c0into = None
        self.c0away = None
        self.c3help = None
        self.c1ploy = None
        # 登录赋值_mt5
        self.mt5_login = 00000000000000000  # TODO
        self.mt5_password = "00000000000000000"  # TODO
        self.mt5_server = "00000000000000000"  # TODO
        # 登录赋值_邮箱
        self.email_addr_from = "00000000000000000"
        self.email_addr_to = self.email_addr_from
        self.email_smtp_host = "smtp.qq.com"
        self.email_smtp_port = 465
        self.email_smtp_password = "00000000000000000"
        # 综合赋值
        self.log = C1Help(symbol).d0log
        self.title = C1Help(symbol).d0title

    @staticmethod
    def d0config_independent():
        """ 需要单独配置的模块等
        """
        # pandas
        pandas.set_option('display.max_columns', None)  # 显示列数, None:显示所有列
        pandas.set_option('display.max_rows', 30)  # 显示行数, None:显示所有行
        pandas.set_option('max_colwidth', 200)  # 数据长度，默认50字节
        pandas.set_option('expand_frame_repr', False)  # 设置换行, False:不换行，True:换行
        # colorama
        colorama.init(autoreset=True)

    def d0config_connect(self):
        """ 连接mt5/设置标的/显示标的
        # 如果无法自动找到MT5的安装路径, 则需要在MetaTrader5.initialize()的括号内部自行输入: r"MT5的绝对安装路径"
        """
        while not MetaTrader5.initialize():
            time.sleep(self.secs_middle)
        if not MetaTrader5.login(login=self.mt5_login, password=self.mt5_password, server=self.mt5_server):
            self.log("$配置连接$ 登录失败: 直接退出进程", level="error")
            quit()
        symbol = MetaTrader5.symbol_info(self.symbol)
        if symbol is None:
            self.log("$配置连接$ 找不到标的: 直接退出进程", level="error")
            quit()
        if not symbol.visible:
            if not MetaTrader5.symbol_select(self.symbol, True):
                self.log("$配置连接$ 无法显示标的: 直接退出进程", level="error")
                quit()

    def d0config_instance(self):
        """ 实例化所有主类
        """
        self.c1help = C1Help(symbol=self.symbol)
        self.c2help = C2Help(c1help=self.c1help,
                             symbol=self.symbol,
                             secs_short=self.secs_short,
                             secs_middle=self.secs_middle,
                             secs_long=self.secs_long,
                             secs_super=self.secs_super,
                             email_addr_from=self.email_addr_from,
                             email_addr_to=self.email_addr_to,
                             email_smtp_host=self.email_smtp_host,
                             email_smtp_port=self.email_smtp_port,
                             email_smtp_password=self.email_smtp_password)
        self.c0into = C0Into(c1help=self.c1help,
                             symbol=self.symbol,
                             bar_frame=self.bar_frame)
        self.c0away = C0Away(c1help=self.c1help,
                             c2help=self.c2help,
                             c0into=self.c0into,
                             symbol=self.symbol,
                             decimal=self.decimal,
                             fail_max=self.fail_max)
        self.c3help = C3Help(c1help=self.c1help,
                             c2help=self.c2help,
                             c0into=self.c0into,
                             c0away=self.c0away,
                             symbol=self.symbol,
                             decimal=self.decimal,
                             balance_begin=self.balance_begin,
                             balance_margin=self.balance_margin,
                             balance_shrink=self.balance_shrink)
        self.c1ploy = C1Ploy(c1help=self.c1help,
                             c2help=self.c2help,
                             c0into=self.c0into,
                             c0away=self.c0away,
                             c3help=self.c3help,
                             symbol=self.symbol,
                             decimal=self.decimal,
                             bar_frame=self.bar_frame)

    def d0config_all(self):
        """ 配置前面的所有项目
        """
        self.d0config_independent()
        self.d0config_connect()
        self.d0config_instance()

    def d0common_start(self):
        """ 适用于所有进程的启动信息
        """
        self.log(self.title("通用启动", position="up"))
        self.d0config_all()
        self.c3help.d0toolbox_common()
        self.log(self.title("账户信息", position="up", sub=True))
        self.log(f"\n{self.c0into.d0account_info()}")
        self.log(self.title("通用信息", position="up", sub=True))
        self.log(f"综合: "
                 f"小数={self.decimal}位, "
                 f"期初={self.balance_begin}USD, "
                 f"连败={self.fail_max}次")
        self.log(f"时长: "
                 f"较短={timedelta(seconds=self.secs_short)}, "
                 f"中等={timedelta(seconds=self.secs_middle)}, "
                 f"较长={timedelta(seconds=self.secs_long)}, "
                 f"超长={timedelta(seconds=self.secs_super)}")
        self.log(self.title("通用启动", position="down"))

    def d0common_quit(self):
        """ 当所有策略/进程退出之后显示的信息
        """
        self.log(self.title("通用退出", position="up"))
        self.d0config_all()
        self.log(f"\n{self.c0into.d0account_info()}")
        self.log(self.title("通用退出", position="down"))

    def d0ploy_start(self):
        """ 启动策略
        """
        self.d0config_all()
        self.c1ploy.d0circle_center()

    def d0ploy_quit(self):
        """ 退出策略
        """
        self.d0config_all()
        self.c3help.d0toolbox_blank()
        self.log(f"~退出策略~ 最后错误={str(MetaTrader5.last_error())}", level="error")
        self.log("$退出策略$", level="warning")
        quit()
