import time

class StockModel:
    def __init__(self, code, codename, baldongprice, sigapercent, dongjeokprice, jeongjeokprice, gererayng, memetime, virelease, vibaldongcount, vigubun, vipoint, vitype, won_to_buy):
        self.firstbuytime = time.time()
        self.ALLOW_AUTO_BUYSELL = True
        self.n_BUY_DONE = False
        self.n_code = code
        self.n_codename = codename
        self.n_baldongprice = baldongprice
        self.n_sigapercent = sigapercent
        self.n_dongjeokprice = dongjeokprice
        self.n_jeongjeokprice = jeongjeokprice
        self.n_gererayng = gererayng
        self.n_memetime = memetime
        self.n_virelease = virelease
        self.n_vibaldongcount = vibaldongcount
        self.n_vigubun = vigubun
        self.n_vipoint = vipoint
        self.n_vitype = vitype
        self.firstbuy_price = '0'
        self.req_time = '-'
        self.res_time = '-'
        self.order_no = '-'
        self.stock_code = code
        self.stock_name = codename
        self.stock_count = 0
        self.stock_contractcount = 0
        self.stock_yet_count = 0
        self.buy_cost = 0
        self.sell_cost = 0
        self.cur_cost = 0
        self.profit = 0
        self.profit_per = 0
        self.status = '-'
        self.sell_plus_1_done = False
        self.sell_plus_1_price = 0
        self.sell_plus_2_done = False
        self.sell_plus_2_price = 0
        self.sell_plus_3_done = False
        self.sell_plus_3_price = 0
        self.sell_plus_4_done = False
        self.sell_plus_4_price = 0
        self.sell_plus_5_done = False
        self.sell_plus_5_price = 0
        self.sell_plus_6_done = False
        self.sell_plus_6_price = 0
        self.sell_plus_7_done = False
        self.sell_plus_7_price = 0
        self.medohoga5 = 0
        self.medohoga10 = 0
        self.sichong = 0
        self.n_won_to_buy = won_to_buy

    def bought(self, ALLOW_AUTO_BUYSELL, firstbuy_price, req_time, res_time, order_no, stock_count, stock_contractcount, stock_yet_count, buy_cost, sell_cost, cur_cost, profit, profit_per, status):
        self.n_firstbuytime = time.time()
        self.ALLOW_AUTO_BUYSELL = ALLOW_AUTO_BUYSELL
        self.firstbuy_price = firstbuy_price
        self.req_time = req_time
        self.res_time = res_time
        self.order_no = order_no
        self.stock_count = stock_count
        self.stock_contractcount = stock_contractcount
        self.stock_yet_count = stock_yet_count
        self.buy_cost = buy_cost
        self.sell_cost = sell_cost
        self.cur_cost = cur_cost
        self.profit = profit
        self.profit_per = profit_per
        self.status = status
        self.sell_plus_1_done = False
        self.sell_plus_1_price = 0
        self.sell_plus_2_done = False
        self.sell_plus_2_price = 0
        self.sell_plus_3_done = False
        self.sell_plus_3_price = 0
        self.sell_plus_4_done = False
        self.sell_plus_4_price = 0
        self.sell_plus_5_done = False
        self.sell_plus_5_price = 0
        self.sell_plus_6_done = False
        self.sell_plus_6_price = 0
        self.sell_plus_7_done = False
        self.sell_plus_7_price = 0
        self.medohoga5 = 0
        self.medohoga10 = 0
        self.sichong = 0

    def __str__(self):
        return f"[StockModel] 요청시간: {self.req_time}, 체결시간: {self.res_time}, 주문번호: {self.order_no}, 코드: {self.stock_code}, 종목: {self.stock_name}, 수량: {self.stock_count}, 체결수량: {self.stock_contractcount}, 미체결수량: {self.stock_yet_count}, 매수가: {self.buy_cost}, 매도가: {self.sell_cost}, 현재가: {self.cur_cost}, 평가손익: {self.profit}, 수익률(%): {self.profit_per}, 상태: {self.status}"
