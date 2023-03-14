import time
from math import trunc
from PyQt5 import QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QDoubleSpinBox

import common
from stock_model import StockModel

class MyStock:
    def __init__(self, caller):
        self.caller = caller
        self.my_stocks = []
        self.name = "MYSTOCK"

    def clear_all_stocks(self):
        self.my_stocks.clear()

    # 계좌평가잔고내역요청
    def add_stock_from_account(self, stock_code, stock_name, stock_quantity, stock_buy_money, stock_present_price, stock_evaluation_profit_and_loss, stock_yield):
        new_News = StockModel(stock_code, stock_name, '0', '0', '0', '0', '0', '0', '0', '-', '-', '0', '-', '0', '-', self.caller.BUY_MINIMUM_COST_MANWON)
        self.my_stocks.insert(0, new_News)
        self.my_stocks[0].n_BUY_DONE = True
        self.my_stocks[0].bought(False, stock_buy_money, '-', '-', '-', stock_quantity, 0, 0, stock_buy_money, 0, stock_present_price, stock_evaluation_profit_and_loss, stock_yield, '정상')
        self.insert_to_stock_table(self.my_stocks[0])
        print(f'{common.getCurDateTime()}_[{self.name}][MyStock] add_stock_from_account, {self.my_stocks[0].stock_code}, {self.my_stocks[0].stock_name}, {self.my_stocks[0].stock_count}, {self.my_stocks[0].status}')

    def updateBalanceToTable(self, codename, totalcount, avgcost):
        print(f'{common.getCurDateTime()}_[{self.name}][MyStock][updateBalanceToTable] updateBalanceToTable, {codename}, {type(codename)}, {totalcount}, {type(totalcount)}, {avgcost}, {type(avgcost)}')
        if int(totalcount) == 0:
            for row in range(self.caller.tableWidget.rowCount()):
                item = self.caller.tableWidget.item(row, self.caller.COL_NAME)
                if item is not None and codename == item.text():
                    # self.caller.tableWidget2.setItem(row, 7, QTableWidgetItem(common.convertNumberToMoney(avgcost)))
                    # 회색처리
                    self.caller.tableWidget.setItem(row, self.caller.COL_COUNT_BOUGHT, QTableWidgetItem(totalcount))
                    self.caller.setColorEmptyRow(row, QtGui.QColor(150, 150, 150, 200))
                    break
            for mydata in self.my_stocks:
                if mydata.stock_name == codename:
                    print(f'{common.getCurDateTime()}_[{self.name}][MyStock][updateBalanceToTable] removeRealTimeRegCode call: {codename}')
                    mydata.stock_count = int(totalcount)
                    # 실시간등록 해제
                    self.caller.KIWOOM.removeRealTimeRegCode(self.caller.kospi_dic_by_name_main.get(codename, '-'))
                    # 리스트에서 삭제
                    self.my_stocks.remove(mydata)
                    # 테이블에서 삭제
                    # self.remove_from_stock_table(mydata)
                    break
        else:
            for row in range(self.caller.tableWidget.rowCount()):
                item = self.caller.tableWidget.item(row, self.caller.COL_NAME)
                if item is not None and codename == item.text():
                    # self.caller.tableWidget.setItem(row, self.caller.COL_BALDONG_PRICE, QTableWidgetItem('+0'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_COUNT_BOUGHT, QTableWidgetItem(totalcount))
                    self.caller.tableWidget.setItem(row, self.caller.COL_BUY_PRICE, QTableWidgetItem(common.convertNumberToMoney(avgcost)))
                    break
            for mydata in self.my_stocks:
                if mydata.stock_name == codename:
                    mydata.stock_count = int(totalcount)
                    mydata.buy_cost = int(avgcost)
                    break

    def add_or_update_stock(self, sell_or_buy, req_time, res_time, order_no, stock_code, stock_name, stock_count,
                            stock_contractcount, stock_yet_count, buy_cost, cur_cost, profit, profit_per, broker, status):
        # sell_or_buy 1: 매도, 2: 매수
        is_new = True
        for model in self.my_stocks:
            if model.stock_code == stock_code:
                is_new = False
                if req_time != '-':
                    model.req_time = req_time
                model.res_time = res_time
                model.status = status
                model.order_no = order_no
                model.stock_yet_count = stock_yet_count
                model.status = status
                if sell_or_buy == "1":
                    model.sell_cost = buy_cost
                else:
                    model.sell_cost = 0
                    model.buy_cost = buy_cost
                self.update_to_stock_table(sell_or_buy, status, model)
                print(f'{common.getCurDateTime()}_[{self.name}][MyStock] add_or_update_stock, UPDATE: {stock_code}, {stock_name}, {stock_count}, {status}')
                break
        if is_new:
            new_News = StockModel(stock_code, stock_name, '0', '0', '0', '0', '0', '0', '0', '-', '-', '0', '-', '0', '-', self.caller.BUY_MINIMUM_COST_MANWON)
            self.my_stocks.insert(0, new_News)
            self.my_stocks[0].bought(True, buy_cost, req_time, res_time, order_no, stock_count,
                                 stock_contractcount, stock_yet_count, buy_cost, cur_cost, profit, profit_per, broker,
                                 status, 0)
            self.insert_to_stock_table(self.my_stocks[0])

            print(f'{common.getCurDateTime()}_[{self.name}][MyStock] add_or_update_stock, NEW: {stock_code}, {stock_name}, {stock_count}, {status}')


                    # if model.stock_count > 0:
                    #     self.update_to_stock_table(model)
                    # else:
                    #     self.remove_from_stock_table(model)
        # else: #매수
        #     for model in self.my_stocks:
        #         if newdata.stock_code == model.stock_code:
        #             is_new = False
        #             model.res_time = newdata.res_time
        #             if model.status == '접수':
        #                 model.stock_yet_count = newdata.stock_yet_count
        #             elif model.status == '체결중':
        #                 model.stock_yet_count = newdata.stock_yet_count
        #                 model.stock_count = model.stock_count + newdata.stock_contractcount
        #             elif model.status == '체결완료':
        #                 model.stock_yet_count = newdata.stock_yet_count
        #                 model.stock_count = model.stock_count + newdata.stock_contractcount
        #             model.buy_cost = newdata.buy_cost
        #             model.cur_cost = newdata.cur_cost
        #             model.profit = newdata.profit
        #             model.profit_per = newdata.profit_per
        #             model.status = newdata.status
        #             self.update_to_stock_table(model)
        #             print(f"[MyStock] add_or_update_stock, UPDATE: {newdata.stock_code}, {newdata.stock_name}, {newdata.stock_count}, {newdata.status}")
        #             break

    def update_realtime_sise(self, stock_code, cur_cost, diff, diff_percent, timewithcolumn):
        if len(self.my_stocks) > 0:
            code_exist = False
            for model in self.my_stocks:
                if stock_code == model.n_code:
                    model.cur_cost = cur_cost
                    first_buy_time = model.firstbuytime
                    if model.stock_count > 0:
                        has_morethan_one = True
                    else:
                        has_morethan_one = False
                    code_exist = True

                    if code_exist and has_morethan_one and model.ALLOW_AUTO_BUYSELL:
                        try:
                            my_count = int(model.stock_count)
                            my_avg = int(model.buy_cost)
                        except:
                            my_count = 0
                            my_avg = 0
                        if( abs(my_avg) >= abs(cur_cost) ):
                            my_tax = 0
                        else:
                            my_tax = (abs(cur_cost)) * 0.0025
                        my_commission = (abs(my_avg)) * 0.00015 + (abs(cur_cost)) * 0.00015 # my_commission = (abs(my_avg)) * 0.0035 + (abs(cur_cost)) * 0.0035
                        try:
                            my_profit_percent = round((abs(model.cur_cost) - my_avg - my_tax - my_commission) / (my_avg - my_tax - my_commission) * 100, 2)
                        except:
                            my_profit_percent = 0

                        # SEC_WAIT_SELL_AFTER_BUY 초 이후부터 매도 시작
                        if (time.time() - model.firstbuytime) > self.caller.SEC_WAIT_SELL_AFTER_BUY:
                            print(f'{common.getCurDateTime()}_[{self.name}][update_realtime_sise] 시세모니터(매도가능:{self.caller.SEC_WAIT_SELL_AFTER_BUY}초), 코드: {stock_code}, 보유수량: {my_count}, 현재가: {model.cur_cost}, 평균가: {my_avg}, 세금: {my_tax}, 수수료: {my_commission}, 수익률: {my_profit_percent}, 익절커트라인: {self.caller.SELL_HIGH_CUTLINE_PERCENT}%, 손절커트라인: {self.caller.SELL_LOW_CUTLINE_PERCENT}%')
                        else:
                            print(f'{common.getCurDateTime()}_[{self.name}][update_realtime_sise] 시세모니터(매도금지:{self.caller.SEC_WAIT_SELL_AFTER_BUY}초), 코드: {stock_code}, 보유수량: {my_count}, 현재가: {model.cur_cost}, 평균가: {my_avg}, 세금: {my_tax}, 수수료: {my_commission}, 수익률: {my_profit_percent}, 익절커트라인: {self.caller.SELL_HIGH_CUTLINE_PERCENT}%, 손절커트라인: {self.caller.SELL_LOW_CUTLINE_PERCENT}%', file=self.caller.viLogFile)

                        if (time.time() - model.firstbuytime) > self.caller.SEC_WAIT_SELL_AFTER_BUY:
                            # 매수 직후 오를 경우
                            # 2% 이상이면 30% 매도,
                            # 4% 이상이면 30% 매도,
                            # 6% 이상이면 30% 매도, 2% 단위로 반복, 전체수량대비 10% 남으면 올 매도 (약 14% 시점)
                            # 직전 매도 % 이하로 내려 가면 올 매도
                            if my_profit_percent > self.caller.SELL_HIGH_CUTLINE_PERCENT and model.sell_plus_1_done is False:
                                model.sell_plus_1_done = True
                                model.sell_plus_1_price = cur_cost
                                to_sell = trunc(my_count * 0.3) - 1
                                self.caller.KIWOOM.stock_sell_single(stock_code, to_sell)
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 1차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%')
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 1차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                                self.caller.PlaySoundEffect("sound_success.wav")
                            elif my_profit_percent > self.caller.SELL_HIGH_CUTLINE_PERCENT * 2 and model.sell_plus_2_done is False:
                                model.sell_plus_2_done = True
                                model.sell_plus_2_price = cur_cost
                                to_sell = trunc(my_count * 0.3) - 1
                                self.caller.KIWOOM.stock_sell_single(stock_code, to_sell)
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 2차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%')
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 2차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                                self.caller.PlaySoundEffect("sound_success.wav")
                            elif my_profit_percent > self.caller.SELL_HIGH_CUTLINE_PERCENT * 3 and model.sell_plus_3_done is False:
                                model.sell_plus_3_done = True
                                model.sell_plus_3_price = cur_cost
                                to_sell = trunc(my_count * 0.3) - 1
                                self.caller.KIWOOM.stock_sell_single(stock_code, to_sell)
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 3차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%')
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 3차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                                self.caller.PlaySoundEffect("sound_success.wav")
                            elif my_profit_percent > self.caller.SELL_HIGH_CUTLINE_PERCENT * 4 and model.sell_plus_4_done is False:
                                model.sell_plus_4_done = True
                                model.sell_plus_4_price = cur_cost
                                to_sell = trunc(my_count * 0.3) - 1
                                self.caller.KIWOOM.stock_sell_single(stock_code, to_sell)
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 4차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%')
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 4차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                                self.caller.PlaySoundEffect("sound_success.wav")
                            elif my_profit_percent > self.caller.SELL_HIGH_CUTLINE_PERCENT * 5 and model.sell_plus_5_done is False:
                                model.sell_plus_5_done = True
                                model.sell_plus_5_price = cur_cost
                                to_sell = trunc(my_count * 0.3) - 1
                                self.caller.KIWOOM.stock_sell_single(stock_code, to_sell)
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 5차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%')
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 5차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                                self.caller.PlaySoundEffect("sound_success.wav")
                            elif my_profit_percent > self.caller.SELL_HIGH_CUTLINE_PERCENT * 6 and model.sell_plus_6_done is False:
                                model.sell_plus_6_done = True
                                model.sell_plus_6_price = cur_cost
                                to_sell = trunc(my_count * 0.3) - 1
                                self.caller.KIWOOM.stock_sell_single(stock_code, to_sell)
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 6차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%')
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 6차 익절, {to_sell}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                                self.caller.PlaySoundEffect("sound_success.wav")
                            elif my_profit_percent > self.caller.SELL_HIGH_CUTLINE_PERCENT * 7 and model.sell_plus_7_done is False:
                                model.sell_plus_7_done = True
                                model.sell_plus_7_price = cur_cost
                                self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 7차 익절 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%')
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 7차 익절 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                                self.caller.PlaySoundEffect("sound_success.wav")
                            # # 1차 매도 했는데, 시세가 2%보다 내려가면 올 매도
                            # elif model.sell_plus_1_done and my_profit_percent < (self.caller.SELL_HIGH_CUTLINE_PERCENT - 2):
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 1차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT - 2)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%')
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 1차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT - 2)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                            #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            #     self.caller.PlaySoundEffect("sound_success.wav")
                            # # 2차 매도 했는데, 시세가 1차 매수가보다 내려 가면 다 매도
                            # elif model.sell_plus_2_done and my_profit_percent < self.caller.SELL_HIGH_CUTLINE_PERCENT:
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 2차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 2)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%')
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 2차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 2)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                            #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            #     self.caller.PlaySoundEffect("sound_success.wav")
                            # elif model.sell_plus_3_done and my_profit_percent < self.caller.SELL_HIGH_CUTLINE_PERCENT * 2:
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 3차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 3)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%')
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 3차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 3)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                            #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            #     self.caller.PlaySoundEffect("sound_success.wav")
                            # elif model.sell_plus_4_done and my_profit_percent < self.caller.SELL_HIGH_CUTLINE_PERCENT * 3:
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 4차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 4)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%')
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 4차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 4)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                            #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            #     self.caller.PlaySoundEffect("sound_success.wav")
                            # elif model.sell_plus_5_done and my_profit_percent < self.caller.SELL_HIGH_CUTLINE_PERCENT * 4:
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 5차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 5)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%')
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 5차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 5)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                            #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            #     self.caller.PlaySoundEffect("sound_success.wav")
                            # elif model.sell_plus_6_done and my_profit_percent < self.caller.SELL_HIGH_CUTLINE_PERCENT * 5:
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 6차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 6)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%')
                            #     print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, 6차 {(self.caller.SELL_HIGH_CUTLINE_PERCENT * 6)}% 시점 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                            #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            #     self.caller.PlaySoundEffect("sound_success.wav")

                            # SELL_LOW_CUTLINE_PERCENT% 이하 내려 가면 전량 매도
                            elif my_profit_percent < self.caller.SELL_LOW_CUTLINE_PERCENT:
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, {(self.caller.SELL_LOW_CUTLINE_PERCENT)}% 커트라인 도달, 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%')
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, {(self.caller.SELL_LOW_CUTLINE_PERCENT)}% 커트라인 도달, 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%', file=self.caller.viLogFile)
                                self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                                self.caller.PlaySoundEffect("sound_fail.wav")
                            # x초 이후 에도 -1% < 매수가 < 2% 사이일 경우 전량 매도
                            elif my_profit_percent > self.caller.SELL_LOW_CUTLINE_PERCENT and my_profit_percent < self.caller.SELL_HIGH_CUTLINE_PERCENT and (time.time() - first_buy_time) > self.caller.SELL_CUTLINE_TIMESEC:
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, {self.caller.SELL_HIGH_CUTLINE_PERCENT}% 와 {(self.caller.SELL_HIGH_CUTLINE_PERCENT)}% 사이에서, {(time.time() - first_buy_time)} 시간 소모 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%, 시간 커트라인: {self.caller.SELL_CUTLINE_TIMESEC}')
                                print(f'{common.getCurDateTime()}_[{self.name}] {stock_code}, {self.caller.SELL_HIGH_CUTLINE_PERCENT}% 와 {(self.caller.SELL_HIGH_CUTLINE_PERCENT)}% 사이에서, {(time.time() - first_buy_time)} 시간 소모 전량 매도, {my_count}주, 퍼센트: {my_profit_percent}%, 시간 커트라인: {self.caller.SELL_CUTLINE_TIMESEC}', file=self.caller.viLogFile)
                                self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                                self.caller.PlaySoundEffect("sound_fail.wav")

                            # # 평균수익 -1% 이하면 30% 매도
                            # # 평균수익 -2% 이하면 올 매도 // 50% 매도
                            # # // 평균수익 -3% 이하면 올 매도
                            # # elif model.sell_plus_3_done and model.sell_plus_2_price < cur_cost:
                            # #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            # # elif model.sell_plus_2_done and model.sell_plus_1_price < cur_cost:
                            # #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            # elif my_profit_percent < -1 and model.sell_minus_1_done is False:
                            #     model.sell_minus_1_done = True
                            #     to_sell = trunc(my_count * 0.5) - 1
                            #     self.caller.KIWOOM.stock_sell_single(stock_code, to_sell)
                            # elif my_profit_percent < -1.5 and model.sell_minus_2_done is False:
                            #     model.sell_minus_2_done = True
                            #     # to_sell = trunc(my_count * 0.5) - 1
                            #     # self.caller.KIWOOM.stock_sell_single(stock_code, to_sell)
                            #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            # # elif my_profit_percent < -3 and model.sell_minus_3_done is False:
                            # #     model.sell_minus_3_done = True
                            # #     self.caller.KIWOOM.stock_sell_all(stock_code, my_count, self.caller.buy_sell_screen_no)
                            # print(f'[update_realtime_sise] 4')
                    break
            if code_exist:
                for row in range(len(self.my_stocks)): #self.caller.tableWidget2.rowCount()):
                    try:
                        # column_headers = ['요청시간', '체결시간', '주문번호', '코드', '종목', '수량', '미체결', '매수가', '매도가', '현재가', '평가손익', '수익률(%)', '상태', '매도']
                        item = self.caller.tableWidget.item(row, self.caller.COL_CODE).text()
                        # 0주이상일때만 업데이트
                        if stock_code == item and has_morethan_one:
                            # 현재가
                            new_cprice = format(abs(int(cur_cost)), ',')
                            new_diff = format(int(diff), ',')
                            new_diffpercent = diff_percent
                            new_iconup = '▲'
                            new_icondown = '▼'
                            # print(f'{common.getCurDateTime()}_[{self.name}][update_realtime_sise] {timewithcolumn}, stock_code {stock_code}, new_cprice {new_cprice}, new_diff {new_diff}, new_diffpercent {new_diffpercent}')
                            if float(diff) > 0:
                                cur_price_str = new_cprice + ' ' + new_iconup + ' (' + new_diff + ') ' + new_diffpercent + '%'
                                item = QTableWidgetItem(cur_price_str)
                                item.setForeground(QtGui.QColor(250, 50, 0, 250))
                                item.setBackground(QtGui.QColor(250, 0, 0, 25))
                            else:
                                cur_price_str = new_cprice + ' ' + new_icondown + ' (' + new_diff + ') ' + new_diffpercent + '%'
                                item = QTableWidgetItem(cur_price_str)
                                item.setForeground(QtGui.QColor(0, 50, 250, 250))
                                item.setBackground(QtGui.QColor(0, 0, 250, 25))
                            self.caller.tableWidget.setItem(row, self.caller.COL_CUR_PRICE, item)
                            my_count = int(self.caller.tableWidget.item(row, self.caller.COL_COUNT_BOUGHT).text())
                            my_avg = int(self.caller.tableWidget.item(row, self.caller.COL_BUY_PRICE).text().replace(',', ''))
                            # 8 평가손익  현재가*보유량 - 매수가*보유량
                            tax = (abs(cur_cost) * my_count) * 0.0023
                            commission = (abs(cur_cost) * my_count) * 0.00015
                            profit = (abs(cur_cost) * my_count) - (my_avg * my_count) - tax - commission
                            item = QTableWidgetItem(common.convertNumberToMoney(profit))
                            if profit > 0:
                                item.setForeground(QtGui.QColor(250, 50, 0, 250))
                                item.setBackground(QtGui.QColor(250, 0, 0, 25))
                            else:
                                item.setForeground(QtGui.QColor(0, 50, 250, 250))
                                item.setBackground(QtGui.QColor(0, 0, 250, 25))
                            self.caller.tableWidget.setItem(row, self.caller.COL_PROFIT_PRICE, item)
                            # 9 수익률  (현재가 - 구매가) / 구매가 * 100
                            if my_avg > 0:
                                tax2 = abs(cur_cost) * 0.0023
                                commission2 = abs(cur_cost) * 0.00015
                                profit_percent = round((abs(cur_cost) - my_avg - tax2 - commission2) / (my_avg - tax2 - commission2) * 100, 2)
                                ##### 자동매도 #####
                                # if allow_autosell:
                                #     # print(f'[update_realtime_sise] autosell call, stock_code {stock_code}')
                                #     self.autoSell(stock_code, profit_percent, my_count, first_buy_time)
                                # else:
                                #     print(f'[update_realtime_sise] autosell pass for, stock_code {stock_code}')
                            else:
                                profit_percent = '-'
                            item = QTableWidgetItem(str(profit_percent) + '%')
                            if my_avg > 0:
                                if profit_percent > 0:
                                    item.setForeground(QtGui.QColor(250, 50, 0, 250))
                                    item.setBackground(QtGui.QColor(250, 0, 0, 25))
                                else:
                                    item.setForeground(QtGui.QColor(0, 50, 250, 250))
                                    item.setBackground(QtGui.QColor(0, 0, 250, 25))
                            self.caller.tableWidget.setItem(row, self.caller.COL_PROFIT_PERCENT, item)
                            # self.caller.tableWidget.resizeRowsToContents()
                            break
                    except Exception as e:
                        print(f'{common.getCurDateTime()}_[{self.name}][update_realtime_sise] Exception on: {e}')

    # def autoSell(self, stock_code, profit_percent, my_count, first_buy_time):
    #     if profit_percent <= self.caller.SELL_LOW_CUTLINE_PERCENT:
    #         print(f'{common.getCurDateTime()}_[{self.name}][autoSell] SELL_LOW_CUTLINE_PERCENT: stock_code:{stock_code}, profit_percent:{profit_percent}, my_count:{my_count}')
    #         self.caller.KIWOOM.stock_sell_single(stock_code, my_count)
    #     elif profit_percent >= self.caller.SELL_HIGH_CUTLINE_PERCENT:
    #         print(f'{common.getCurDateTime()}_[{self.name}][autoSell] SELL_HIGH_CUTLINE_PERCENT: stock_code:{stock_code}, profit_percent:{profit_percent}, my_count:{my_count}')
    #         self.caller.KIWOOM.stock_sell_single(stock_code, my_count)
    #     elif profit_percent > self.caller.SELL_LOW_CUTLINE_PERCENT and profit_percent < self.caller.SELL_HIGH_CUTLINE_PERCENT and (time.time() - first_buy_time) >= self.caller.SELL_CUTLINE_TIMESEC:
    #         print(f'{common.getCurDateTime()}_[{self.name}][autoSell] SELL_CUTLINE_TIMESEC: stock_code:{stock_code}, profit_percent:{profit_percent}, my_count:{my_count}, first_buy_time:{first_buy_time}, timepassed:{(time.time() - first_buy_time)}')
    #         self.caller.KIWOOM.stock_sell_single(stock_code, my_count)

    def insert_to_stock_table(self, data):
        row = 0 #self.caller.tableWidget2.rowCount()
        print(f'{common.getCurDateTime()}_[{self.name}][insert_to_stock_table] row count: ', str(row))
        #column_headers = ['코드', '종목명', '시가대비\n등락률', '기준가격\n동적VI', '기준가격\n정적VI', '거래량', '발동', '해지', '발동가격', '호가',
        #                  '횟수', 11'주문번호', 12'수량', 13'미체결', 14'매수가', '매도가', 16'현재가', '평가손익', '수익률', '상태', '매도', '매도']
        self.caller.tableWidget.insertRow(row)
        self.caller.tableWidget.setItem(row, self.caller.COL_CODE, QTableWidgetItem(data.stock_code))
        self.caller.tableWidget.setItem(row, self.caller.COL_NAME, QTableWidgetItem(data.stock_name))
        self.caller.tableWidget.setItem(row, self.caller.COL_SIGA_PERCENT, QTableWidgetItem(data.n_sigapercent))
        self.caller.tableWidget.setItem(row, self.caller.COL_PRICE_DONGJEOK, QTableWidgetItem(data.n_dongjeokprice))
        self.caller.tableWidget.setItem(row, self.caller.COL_PRICE_JUNGJEOK, QTableWidgetItem(data.n_dongjeokprice))
        self.caller.tableWidget.setItem(row, self.caller.COL_GERRERAYNG, QTableWidgetItem(data.n_gererayng))
        self.caller.tableWidget.setItem(row, self.caller.COL_BALDONG_TIME, QTableWidgetItem(data.n_memetime))
        self.caller.tableWidget.setItem(row, self.caller.COL_HEJI_TIME, QTableWidgetItem(data.n_virelease))
        self.caller.tableWidget.setItem(row, self.caller.COL_BALDONG_PRICE, QTableWidgetItem(data.n_baldongprice))
        self.caller.tableWidget.setItem(row, self.caller.COL_HOGA, QTableWidgetItem('-'))
        self.caller.tableWidget.setItem(row, self.caller.COL_VI_COUNT, QTableWidgetItem(data.n_vibaldongcount))
        self.caller.tableWidget.setItem(row, self.caller.COL_ORDERNUM, QTableWidgetItem(data.order_no))
        self.caller.tableWidget.setItem(row, self.caller.COL_COUNT_BOUGHT, QTableWidgetItem(str(data.stock_count)))
        self.caller.tableWidget.setItem(row, self.caller.COL_COUNT_NOTYET, QTableWidgetItem(str(data.stock_yet_count)))
        self.caller.tableWidget.setItem(row, self.caller.COL_BUY_PRICE, QTableWidgetItem(common.convertNumberToMoney(data.buy_cost)))

        if data.cur_cost == '-':
            item = QTableWidgetItem('-')
        else:
            item = QTableWidgetItem(common.convertNumberToMoney(data.cur_cost))
            if int(data.cur_cost) > 0:
                item.setForeground(QtGui.QColor(250, 50, 0, 250))
                item.setBackground(QtGui.QColor(250, 0, 0, 25))
            else:
                item.setForeground(QtGui.QColor(0, 50, 250, 250))
                item.setBackground(QtGui.QColor(0, 0, 250, 25))
        self.caller.tableWidget.setItem(row, self.caller.COL_CUR_PRICE, item)

        if data.profit == '-':
            item = QTableWidgetItem('-')
        else:
            item = QTableWidgetItem(common.convertNumberToMoney(data.profit))
            if int(data.profit) > 0:
                item.setForeground(QtGui.QColor(250, 50, 0, 250))
                item.setBackground(QtGui.QColor(250, 0, 0, 25))
            else:
                item.setForeground(QtGui.QColor(0, 50, 250, 250))
                item.setBackground(QtGui.QColor(0, 0, 250, 25))
        self.caller.tableWidget.setItem(row, self.caller.COL_PROFIT_PRICE, item)

        try:
            item = QTableWidgetItem(str(round(float(data.profit_per), 2)) + '%')
            if float(data.profit_per) > 0:
                item.setForeground(QtGui.QColor(250, 50, 0, 250))
                item.setBackground(QtGui.QColor(250, 0, 0, 25))
            else:
                item.setForeground(QtGui.QColor(0, 50, 250, 250))
                item.setBackground(QtGui.QColor(0, 0, 250, 25))
        except:
            item = QTableWidgetItem('-%')
        self.caller.tableWidget.setItem(row, self.caller.COL_PROFIT_PERCENT, item)
        self.caller.tableWidget.setItem(row, self.caller.COL_STATUS, QTableWidgetItem(data.status))

        self.caller.spinboxToBuy = QDoubleSpinBox()
        self.caller.spinboxToBuy.setMinimum(10)
        self.caller.spinboxToBuy.setMaximum(1000)
        self.caller.spinboxToBuy.setSingleStep(10)
        self.caller.spinboxToBuy.setValue(50)
        self.caller.spinboxToBuy.valueChanged.connect(self.caller.spintoBuyClicked)
        self.caller.tableWidget.setCellWidget(row, self.caller.COL_WON_TO_BUY, self.caller.spinboxToBuy)

        self.caller.buyBtn = QPushButton("매수")
        self.caller.buyBtn.clicked.connect(self.caller.buyClicked)
        self.caller.buyBtn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (250, 50, 0, 255, 255, 255))
        self.caller.tableWidget.setCellWidget(row, self.caller.COL_BTN_MESU, self.caller.buyBtn)

        self.caller.sell30Btn = QPushButton("30%")
        self.caller.sell30Btn.clicked.connect(self.caller.sell30Clicked)
        self.caller.sell30Btn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 50, 200, 255, 255, 255))
        self.caller.tableWidget.setCellWidget(row, self.caller.COL_BTN_MEDO30, self.caller.sell30Btn)

        self.caller.sellAllBtn = QPushButton("100%")
        self.caller.sellAllBtn.clicked.connect(self.caller.sellAllClicked)
        self.caller.sellAllBtn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 50, 250, 255, 255, 255))
        self.caller.tableWidget.setCellWidget(row, self.caller.COL_BTN_MEDO100, self.caller.sellAllBtn)

        if data.ALLOW_AUTO_BUYSELL:
            self.caller.authBtn = QPushButton("오토")
            self.caller.authBtn.clicked.connect(self.caller.autoClicked)
            self.caller.authBtn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 200, 0, 255, 255, 255))
            self.caller.tableWidget.setCellWidget(row, self.caller.COL_BTN_AUTO, self.caller.authBtn)
        else:
            self.caller.authBtn = QPushButton("중지")
            self.caller.authBtn.clicked.connect(self.caller.autoClicked)
            self.caller.authBtn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 0, 0, 255, 255, 255))
            self.caller.tableWidget.setCellWidget(row, self.caller.COL_BTN_AUTO, self.caller.authBtn)

        self.caller.tableWidget.scrollToTop()
        self.caller.tableWidget.resizeRowsToContents()

    def update_to_stock_table(self, sell_or_buy, status, data):
        # sell_or_buy 1: 매도, 2: 매수
        for row in range(len(self.my_stocks)): #self.caller.tableWidget2.rowCount()):
            item = self.caller.tableWidget.item(row, self.caller.COL_CODE)
            if item is not None and data.stock_code == item.text():
                print(f'{common.getCurDateTime()}_[{self.name}][update_to_stock_table] selected code: {data.stock_code}, {row}, {data.order_no}, data.stock_yet_count: {data.stock_yet_count}, data.status: {data.status}')
                self.caller.tableWidget.setItem(row, self.caller.COL_ORDERNUM, QTableWidgetItem(data.order_no))
                # self.caller.tableWidget.setItem(row, self.caller.COL_COUNT_BOUGHT, QTableWidgetItem(str(data.stock_count)))
                self.caller.tableWidget.setItem(row, self.caller.COL_COUNT_NOTYET, QTableWidgetItem(str(data.stock_yet_count)))
                if sell_or_buy == "1":
                    self.caller.tableWidget.setItem(row, self.caller.COL_SELL_PRICE, QTableWidgetItem(common.convertNumberToMoney(data.sell_cost)))
                else:
                    self.caller.tableWidget.setItem(row, self.caller.COL_BUY_PRICE, QTableWidgetItem(common.convertNumberToMoney(data.buy_cost)))
                # item = QTableWidgetItem(common.convertNumberToMoney(data.cur_cost))
                # if int(data.cur_cost) > 0:
                #     item.setForeground(QtGui.QColor(250, 50, 0, 250))
                #     item.setBackground(QtGui.QColor(250, 0, 0, 25))
                # else:
                #     item.setForeground(QtGui.QColor(0, 50, 250, 250))
                #     item.setBackground(QtGui.QColor(0, 0, 250, 25))
                # self.caller.tableWidget.setItem(row, self.caller.COL_BALDONG_PRICE, item)
                #
                # item = QTableWidgetItem(self.caller.convertNumberToMoney(data.profit))
                # if int(data.profit) > 0:
                #     item.setForeground(QtGui.QColor(250, 50, 0, 250))
                #     item.setBackground(QtGui.QColor(250, 0, 0, 25))
                # else:
                #     item.setForeground(QtGui.QColor(0, 50, 250, 250))
                #     item.setBackground(QtGui.QColor(0, 0, 250, 25))
                # self.caller.tableWidget.setItem(row, self.caller.COL_HOGA, item)
                #
                # try:
                #     item = QTableWidgetItem(str(round(float(data.profit_per), 2)) + '%')
                #     if float(data.profit_per) > 0:
                #         item.setForeground(QtGui.QColor(250, 50, 0, 250))
                #         item.setBackground(QtGui.QColor(250, 0, 0, 25))
                #     else:
                #         item.setForeground(QtGui.QColor(0, 50, 250, 250))
                #         item.setBackground(QtGui.QColor(0, 0, 250, 25))
                # except:
                #     item = QTableWidgetItem('-%')
                # self.caller.tableWidget.setItem(row, self.caller.COL_VI_COUNT, item)
                # self.caller.tableWidget.setItem(row, self.caller.COL_ORDERNUM, QTableWidgetItem(data.broker))

                item = QTableWidgetItem(data.status)
                if data.status == '정상':
                    item.setBackground(QtGui.QColor(0, 200, 0, 100))
                elif data.status == '접수':
                    item.setBackground(QtGui.QColor(200, 200, 0, 100))
                elif data.status == '체결중':
                    item.setBackground(QtGui.QColor(250, 50, 0, 100))
                elif data.status == '체결완료':
                    item.setBackground(QtGui.QColor(0, 50, 250, 100))
                    button = self.caller.tableWidget.cellWidget(row, self.caller.COL_BTN_MESU)
                    button.setText('매수')
                    button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (250, 50, 0, 255, 255, 255))
                    button = self.caller.tableWidget.cellWidget(row, self.caller.COL_BTN_MEDO30)
                    button.setText('30%')
                    button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 50, 200, 255, 255, 255))
                    button = self.caller.tableWidget.cellWidget(row, self.caller.COL_BTN_MEDO100)
                    button.setText('100%')
                    button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 50, 250, 255, 255, 255))

                self.caller.tableWidget.setItem(row, self.caller.COL_STATUS, item)
                # self.caller.tableWidget.resizeRowsToContents()
                break

    def remove_from_stock_table(self, data):
        # remove from table
        for row in range(self.caller.tableWidget.rowCount()):
            item = self.caller.tableWidget.item(row, self.caller.COL_CODE)
            if item is not None and data.stock_code == item.text():
                self.caller.tableWidget.removeRow(row)
                break
        # remove from kiwoom watch stock
        self.caller.KIWOOM.removeRealTimeRegCode(data.stock_code)
        # remove from self.my_stocks []
        self.my_stocks.remove(data)
        print(f'{common.getCurDateTime()}_[{self.name}][remove_from_stock_table] removed', data)
        self.show_all_stock()

    def show_all_stock(self):
        for stock in self.my_stocks:
            print(f'{common.getCurDateTime()}_[{self.name}] {stock}')