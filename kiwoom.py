import time
from math import trunc
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from qtpy import QtGui

import common
from mystock import StockModel

class KiwoomAPI:
    def __init__(self, caller):
        self.login_status = False
        self.login_started = False
        self.caller = caller
        return

    def kiwoomInit(self):
        self.name = "키움"
        self.login_started = True
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.OnEventConnect.connect(self.loginEventConnect)
        self.kiwoom.OnReceiveChejanData.connect(self._receive_chejan_data)
        self.kiwoom.OnReceiveRealData.connect(self.receive_realdata)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)
        self.kiwoom.dynamicCall("CommConnect()")
        self.login_loop = QEventLoop()
        self.loginLoopCallback()
        self.login_loop.exec()
        self.screenNo_hoga = "3000"
        self.screenNo_account = "2000"
        self.screenNo_real = "1000"
        self.screenNo_vi = "1500"
        self.realtime_register_code = []
        self.realWatchCount = 190

    def loginEventConnect(self, err_code):
        try:
            print(f'{common.getCurDateTime()}_[{self.name}][loginEventConnect] login success')
            self.login_status = True
            self.caller.btnServiceStart.setEnabled(True)
            self.caller.btnServiceStart.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 100, 250, 255, 255, 255))
            self.login_loop.exit()
            self.login_started = False
        except:
            print(f'{common.getCurDateTime()}_[{self.name}][loginEventConnect] ErrorCode: ' + str(err_code))
            pass

    def addRealTimeRegCode(self, code):
        try:
            if code not in self.realtime_register_code:
                self.realtime_register_code.append(code)
                print(f'{common.getCurDateTime()}_[{self.name}][addRealTimeRegCode]', code)
        except:
            pass
    def removeRealTimeRegCode(self, code):
        try:
            if code in self.realtime_register_code:
                self.realtime_register_code.remove(code)
                print(f'{common.getCurDateTime()}_[{self.name}][removeRealTimeRegCode] remove code: ' + code + ', realtime_register_code', self.realtime_register_code)
                #실시간 와칭 해제
                self.stopRealtimeMonitor(code, False)
        except:
            pass
    def clearRealTimeRegCode(self):
        try:
            self.realtime_register_code.clear()
        except:
            pass
    def getRealTimeRegCode(self):
        result = ''
        try:
            for code in self.realtime_register_code:
                if len(result) == 0:
                    result = code
                else:
                    result = result + ';' + code
        except:
            pass
        print(f'{common.getCurDateTime()}_[{self.name}][getRealTimeRegCode]', result)
        return result

    # 실시간 잔고 모니터링용
    def startRealtimeMonitor(self):
        codelist = self.getRealTimeRegCode()
        if codelist != '':
            # if len(self.realtime_register_code) == 1:
            print(f'{common.getCurDateTime()}_[{self.name}][키움 실시간감시 시작][최초] codelist:', codelist, 'self.screenNo_real:', self.screenNo_real)
            self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screenNo_real, codelist,
                                    '10;11;12;27;28;311;41;61;45;65;50;70;9001;302;9068;1224;1225;9069', 0)
            # else:
            #     print(f'{common.getCurDateTime()}_[{self.name}][키움 실시간감시 시작][추가] codelist:', codelist, 'self.screenNo_real:', self.screenNo_real)
            #     self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screenNo_real, codelist,
            #                             '10;11;12;27;28;311;41;61;45;65;50;70;9001;302;9068;1224;1225;9069', 1)

    def stopRealtimeMonitor(self, stockcode, all):
        print(f'{common.getCurDateTime()}_[{self.name}][키움 실시간감시 중지] all: {all}, stockcode: {stockcode}')
        if all:
            self.kiwoom.dynamicCall("SetRealRemove(QString, QString)", self.screenNo_real, "ALL")
        else:
            self.kiwoom.dynamicCall("SetRealRemove(QString, QString)", self.screenNo_real, stockcode)

    def getAccountInfo(self, kiwoom_status):
        try:
            if self.login_status:
                kiwoom_status.setText("로그인 성공")
                kiwoom_status.setStyleSheet('color:rgb(%s,%s,%s)' % (100, 100, 255))
                self.account_id = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["USER_ID"])
                self.account_name = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["USER_NAME"])
                account_type = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["GetServerGubun"]) #1: 모의투자

                if account_type == '1':
                    account_type_name = str(account_type) + '모의투자 서버'
                else:
                    account_type_name = str(account_type) + '실거래 서버'
                account_list = self.kiwoom.dynamicCall("GetLoginInfo(QString)", ["ACCNO"])
                self.account_num = ''
                self.account_num_list = account_list.split(';')
                for idx, num in enumerate(self.account_num_list):
                    if len(num) > 0:
                        if idx == 0:
                            self.account_num = num
                        self.caller.kiwoom_acc.addItem(num)
                        print(f'{common.getCurDateTime()}_[{self.name}][getAccountInfo] account_num: ' + str(num))
                self.caller.kiwoom_acc.setCurrentIndex(0)
                print(f'{common.getCurDateTime()}_[{self.name}][getAccountInfo] 현재 계좌번호: ' + str(self.account_num))
                kiwoom_status.setText(self.account_id + ' | ' + self.account_name + ' | ' + account_type_name)
            else:
                kiwoom_status.setText("로그인 안됨")
        except:
            print(f'{common.getCurDateTime()}_[{self.name}][loginEventConnect] getAccountInfo ERROR')
            pass

    def setCurAccountNum(self, acc_num):
        self.account_num = acc_num
        print(f'{common.getCurDateTime()}_[{self.name}][setCurAccountNum] 현재 계좌번호: ' + str(self.account_num))

    def getStockInfoList(self):
        kospi = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])
        kosdaq = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["10"])
        kospi_code_list = kospi.split(';')
        kosdaq_code_list = kosdaq.split(';')
        all_stock_code_list = kospi_code_list + kosdaq_code_list
        print(f'{common.getCurDateTime()}_[{self.name}][getStockInfo] Count - kospi: {len(kospi_code_list)}, kosdaq: {len(kosdaq_code_list)}, ALL: {len(all_stock_code_list)}')
        return all_stock_code_list

    def getStockInfo(self):
        kospi_dic_by_code = {}
        kospi = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])
        kosdaq = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["10"])
        kospi_code_list = kospi.split(';')
        kosdaq_code_list = kosdaq.split(';')
        self.all_stock_code_list = kospi_code_list + kosdaq_code_list
        # print(f'{common.getCurDateTime()}_[{self.name}][getStockInfo] Count - kospi: {len(kospi_code_list)}, kosdaq: {len(kosdaq_code_list)}, ALL: {self.all_stock_code_list}')
        cnt = 0
        for code in self.all_stock_code_list:
            name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [code])
            # print(f'[getStockInfo] {cnt}:{name}:{code}')
            # to dictionary
            kospi_dic_by_code[code] = name
            cnt += 1
        kospi_dic_by_name = dict([(value, key) for key, value in kospi_dic_by_code.items()])
        return kospi_dic_by_name

    def getStockInfo2(self):
        kospi_dic_by_code = {}
        for code in self.all_stock_code_list:
            name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [code])
            kospi_dic_by_code[code] = name
        return kospi_dic_by_code

    def loginLoopCallback(self):
        self.waiting_time = 0
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.loginLoopPrint)
        self.timer.start()

    def loginLoopPrint(self):
        self.waiting_time += 1
        print(f'{common.getCurDateTime()}_[{self.name}][loginLoopPrint] waiting login for ' + str(self.waiting_time))
        if self.login_status is True:
            print(f'{common.getCurDateTime()}_[{self.name}][loginLoopPrint] login done, exit waiting')
            self.timer.stop()
            self.kiwoom.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")
        elif self.waiting_time > 60:
            exit()

    def showAccountWindow(self):
        self.kiwoom.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")

    def receive_realdata(self, code, realtype, realdata):
        if realtype == "주식체결":
            timess = self.GetCommRealData(code, 20)     # 체결시간
            cprice = self.GetCommRealData(code, 10)     # 현재가
            diff = self.GetCommRealData(code, 11)       # 전일대비
            acc_vol = self.GetCommRealData(code, 13)    # 누적거래량
            diffpercent = self.GetCommRealData(code, 12)# 등략률
            acc_tvol = self.GetCommRealData(code, 14)   # 누적거래대금
            cVol = self.GetCommRealData(code, 15)       # 거래량
            diffchar = self.GetCommRealData(code, 25)   # 전일대비기호
            # open = self.GetCommRealData(code, 16)     # 시가 # high = self.GetCommRealData(code, 17) # 고가 # low = self.GetCommRealData(code, 18) # 저가 # turnover = self.GetCommRealData(code, 31) # 거래회전율 # strength = self.GetCommRealData(code, 228)# 체결강도 # gubun = self.GetCommRealData(code, 290)   # 장구분
            sichong = self.GetCommRealData(code, 311) # 시가총액
            first_medo_hoga = self.GetCommRealData(code, 27)  # [27] = (최우선)매도호가
            first_mesu_hoga = self.GetCommRealData(code, 28)  # [28] = (최우선)매수호가

            # 실시간 시세 테이블 반영
            timewithcolumn = timess[:2] + ':' + timess[2:4] + ':' + timess[4:]
            # VI 풀리고 처음 들어오는 체결가로.. 매수 구매 결정
            for idx in range(len(self.caller.MYSTOCK.my_stocks)):
                if self.caller.MYSTOCK.my_stocks[idx].n_code == code:
                    # print(f'{common.getCurDateTime()}_[{self.name}][receive_realdata][매수콜] code: {code}, n_BUY_DONE: {self.caller.MYSTOCK.my_stocks[idx].n_BUY_DONE}, ALLOW_AUTO_BUYSELL: {self.caller.MYSTOCK.my_stocks[idx].ALLOW_AUTO_BUYSELL}, first_medo_hoga: {first_medo_hoga}, n_baldongprice: {self.caller.MYSTOCK.my_stocks[idx].n_baldongprice}, BUY_MINIMUM_COST_WON: {self.caller.BUY_MINIMUM_COST_WON}, n_gererayng: {self.caller.MYSTOCK.my_stocks[idx].n_gererayng}, mesuvi_type: {self.caller.mesuvi_type}, n_vipoint: {self.caller.MYSTOCK.my_stocks[idx].n_vipoint}')
                    if self.caller.MYSTOCK.my_stocks[idx].n_BUY_DONE is False:
                        # 조건 맞으면 첫 매수
                        if self.caller.MYSTOCK.my_stocks[idx].ALLOW_AUTO_BUYSELL:
                            if common.convertStringMoneyToInt(first_medo_hoga) >= int(self.caller.MYSTOCK.my_stocks[idx].n_baldongprice) \
                                    and int(self.caller.MYSTOCK.my_stocks[idx].n_gererayng) >= int(self.caller.BUY_MIN_GERERYANG):
                                self.caller.MYSTOCK.my_stocks[idx].firstbuytime = time.time()
                                buy = False
                                if self.caller.mesuvi_type == 2 and self.caller.MYSTOCK.my_stocks[idx].n_vipoint == '1': # 상승만
                                    buy = True
                                elif self.caller.mesuvi_type == 3 and self.caller.MYSTOCK.my_stocks[idx].n_vipoint == '2': # 하락만
                                    buy = True
                                elif self.caller.mesuvi_type == 1: # 모두
                                    buy = True
                                # print(f'{common.getCurDateTime()}_[{self.name}][receive_realdata][매수콜] buy: {buy}')
                                if buy:
                                    print(f'{common.getCurDateTime()}_[{self.name}][receive_realdata][매수콜] 거래량: {self.caller.MYSTOCK.my_stocks[idx].n_gererayng}, 매도호가: {first_medo_hoga}, > VI발동가: {self.caller.MYSTOCK.my_stocks[idx].n_baldongprice}')
                                    self.caller.MYSTOCK.my_stocks[idx].n_BUY_DONE = True
                                    minimum_manwon = self.caller.MYSTOCK.my_stocks[idx].n_won_to_buy;
                                    minimum_won = minimum_manwon * 10000
                                    count_to_buy = trunc(int(minimum_won / common.convertStringMoneyToInt(first_medo_hoga)))
                                    self.new_stock_buy(self.name, self.caller.kospi_dic_by_code_main.get(code, '-'), code, count_to_buy)
                                    self.caller.PlaySoundEffect("sound_buy.mp3")
                    else:
                        # 이미 있음, 업데이트
                        self.caller.MYSTOCK.update_realtime_sise(code, int(cprice), int(diff), diffpercent, timewithcolumn)
                        # print(f'{common.getCurDateTime()}_[{self.name}][receive_realdata][주식체결] 코드: {code}, 현재가: {int(cprice)}, 차이: {int(diff)}, 최우선 매도호가: {first_medo_hoga}, 최우선 매수호가: {int(first_mesu_hoga)}')
                    break

        elif realtype == "주식호가잔량":
            medo_hoga1 = self.GetCommRealData(code, 41)  # [45] = 매도호가5
            medo_hoga1_count = self.GetCommRealData(code, 61)  # [65] = 매도호가5수량
            # medo_hoga5 = self.GetCommRealData(code, 45)  # [45] = 매도호가5
            # mesu_hoga5_count = self.GetCommRealData(code, 65)  # [65] = 매도호가5수량
            # medo_hoga10 = self.GetCommRealData(code, 50)  # [50] = 매도호가10
            # mesu_hoga10_count = self.GetCommRealData(code, 70)  # [70] = 매도호가10수량
            for row in range(self.caller.tableWidget.rowCount()):
                item = self.caller.tableWidget.item(row, self.caller.COL_CODE)
                if item is not None and code == item.text():
                    try:
                        baldongprice_int = int(self.caller.tableWidget.item(row, self.caller.COL_BALDONG_PRICE).text())
                        medohoga_int = int(medo_hoga1[1:])
                        item = QTableWidgetItem(medo_hoga1 + "(" + medo_hoga1_count + ")")
                        if baldongprice_int <= medohoga_int:
                            item.setForeground(QtGui.QColor(250, 50, 0, 250))
                            item.setBackground(QtGui.QColor(250, 0, 0, 25))
                        else:
                            item.setForeground(QtGui.QColor(0, 50, 250, 250))
                            item.setBackground(QtGui.QColor(0, 0, 250, 25))
                        self.caller.tableWidget.setItem(row, self.caller.COL_HOGA, item)
                        # print(f'{common.getCurDateTime()}_[{self.name}][receive_realdata][주식호가잔량] 업데이트, 매도호가1: {medo_hoga1}, 매수호가1잔량: {medo_hoga1_count}')
                    except Exception as e:
                        print(f'{common.getCurDateTime()}_[{self.name}][receive_realdata][주식호가잔량] Exception" {e}')
                        pass
                    break
            pass
        elif realtype == "VI발동/해제":
            # [9001] = 종목코드, 업종코드 # [302] = 종목명 # [13] = 누적거래량 # [14] = 누적거래대금 # [9068] = VI발동구분 # [9008] = KOSPI, KOSDAQ, 전체구분
            # [9075] = 장전구분 # [1221] = VI 발동가격 # [1223] = 매매체결처리시각 # [1224] = VI해제시각 # [1225] = VI적용구분(정적 / 동적 / 동적 + 정적)
            # [1236] = 기준가격정적 # [1237] = 기준가격동적 # [1238] = 괴리율정적 # [1239] = 괴리율동적 # [1489] = VI발동가등락률 # [1490] = VI발동횟수
            # [9069] = 발동방향구분 # [1279] = Extra Item
            code = self.GetCommRealData(code, 9001)[1:]             #종목코드
            codename = self.GetCommRealData(code, 302).strip()      #종목명
            baldongprice = self.GetCommRealData(code, 1221)
            sigapercent = self.GetCommRealData(code, 1489)
            dongjeokprice = self.GetCommRealData(code, 1237)
            jeongjeokprice = self.GetCommRealData(code, 1236)
            gererayng = self.GetCommRealData(code, 13)
            memetime = self.GetCommRealData(code, 1223)
            vibaldongcount = self.GetCommRealData(code, 1490)
            vigubun = self.GetCommRealData(code, 9068)      #VI발동구분
            vipoint = self.GetCommRealData(code, 9069)      #VI발동방향구분  1: 상승 2 하락
            virelease = self.GetCommRealData(code, 1224)    #VI해제시각
            vitype = self.GetCommRealData(code, 1225)       #VI적용구분(정적,동적,정적+동적)
            is_new_news = True
            vi_index = 0
            for idx in range(len(self.caller.MYSTOCK.my_stocks)):
                if self.caller.MYSTOCK.my_stocks[idx].n_code == code and self.caller.MYSTOCK.my_stocks[idx].n_memetime == memetime:
                    is_new_news = False
                    vi_index = idx
                    break
            # 신규
            if is_new_news is True:
                if '선물' in codename or '옵션' in codename or 'ETA' in codename or 'ETF' in codename or 'ETN' in codename:
                    pass
                else:
                    new_News = StockModel(code, codename, baldongprice, sigapercent, dongjeokprice, jeongjeokprice, gererayng, memetime, virelease, vibaldongcount, vigubun, vipoint, vitype, self.caller.BUY_MINIMUM_COST_MANWON)
                    self.caller.MYSTOCK.my_stocks.insert(0, new_News)
                    print(f'{common.getCurDateTime()}_[{self.name}][receive_realdata][VI발동/해제][신규] 코드: {code}, 종목: {codename}, VI발동구분: {vigubun}, {type(vigubun)}, VI발동방향구분: {vipoint}, VI해제시각: {virelease}, VI적용구분: {vitype}')
                    # 실시간등록
                    self.addRealTimeRegCode(code)
                    self.startRealtimeMonitor()
                    row = 0
                    self.caller.tableWidget.insertRow(row)
                    self.caller.tableWidget.setItem(row, self.caller.COL_CODE, QTableWidgetItem(new_News.n_code))
                    self.caller.tableWidget.setItem(row, self.caller.COL_NAME, QTableWidgetItem(new_News.n_codename))

                    item = QTableWidgetItem(new_News.n_sigapercent)
                    if new_News.n_sigapercent[0] == '+':
                        item.setForeground(QtGui.QColor(250, 50, 0, 250))
                        item.setBackground(QtGui.QColor(250, 0, 0, 25))
                    else:
                        item.setForeground(QtGui.QColor(0, 50, 250, 250))
                        item.setBackground(QtGui.QColor(0, 0, 250, 25))
                    self.caller.tableWidget.setItem(row, self.caller.COL_SIGA_PERCENT, item)

                    item = QTableWidgetItem(new_News.n_dongjeokprice)
                    if int(new_News.n_dongjeokprice) > 0:
                        item.setForeground(QtGui.QColor(250, 50, 0, 250))
                        item.setBackground(QtGui.QColor(250, 0, 0, 25))
                    elif int(new_News.n_dongjeokprice) < 0:
                        item.setForeground(QtGui.QColor(0, 50, 250, 250))
                        item.setBackground(QtGui.QColor(0, 0, 250, 25))
                    self.caller.tableWidget.setItem(row, self.caller.COL_PRICE_DONGJEOK, item)

                    item = QTableWidgetItem(new_News.n_jeongjeokprice)
                    if int(new_News.n_jeongjeokprice) > 0:
                        item.setForeground(QtGui.QColor(250, 50, 0, 250))
                        item.setBackground(QtGui.QColor(250, 0, 0, 25))
                    elif int(new_News.n_jeongjeokprice) < 0:
                        item.setForeground(QtGui.QColor(0, 50, 250, 250))
                        item.setBackground(QtGui.QColor(0, 0, 250, 25))
                    self.caller.tableWidget.setItem(row, self.caller.COL_PRICE_JUNGJEOK, item)

                    self.caller.tableWidget.setItem(row, self.caller.COL_GERRERAYNG, QTableWidgetItem(new_News.n_gererayng))
                    self.caller.tableWidget.setItem(row, self.caller.COL_BALDONG_TIME, QTableWidgetItem(new_News.n_memetime))
                    self.caller.tableWidget.setItem(row, self.caller.COL_HEJI_TIME, QTableWidgetItem(new_News.n_virelease))

                    self.caller.tableWidget.setItem(row, self.caller.COL_BALDONG_PRICE, QTableWidgetItem(new_News.n_baldongprice))
                    self.caller.tableWidget.setItem(row, self.caller.COL_HOGA, QTableWidgetItem('0'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_VI_COUNT, QTableWidgetItem(new_News.n_vibaldongcount))
                    self.caller.tableWidget.setItem(row, self.caller.COL_ORDERNUM, QTableWidgetItem('-'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_COUNT_BOUGHT, QTableWidgetItem('0'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_COUNT_NOTYET, QTableWidgetItem('0'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_BUY_PRICE, QTableWidgetItem('0'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_SELL_PRICE, QTableWidgetItem('0'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_CUR_PRICE, QTableWidgetItem('0'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_PROFIT_PRICE, QTableWidgetItem('0'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_PROFIT_PERCENT, QTableWidgetItem('0'))
                    self.caller.tableWidget.setItem(row, self.caller.COL_STATUS, QTableWidgetItem('VI발동'))

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

                    if vipoint == 2:
                        new_News.ALLOW_AUTO_BUYSELL = False
                        self.caller.authBtn = QPushButton("중지")
                        self.caller.authBtn.clicked.connect(self.caller.autoClicked)
                        self.caller.authBtn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 0, 0, 255, 255, 255))
                        self.caller.tableWidget.setCellWidget(row, self.caller.COL_BTN_AUTO, self.caller.authBtn)
                    elif new_News.ALLOW_AUTO_BUYSELL:
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
                    # self.caller.tableWidget.resizeRowsToContents()

                    self.caller.PlaySoundEffect("sound_vi_start.wav")

            else:
                self.caller.PlaySoundEffect("sound_vi_end.wav")
                item = self.caller.tableWidget.item(vi_index, self.caller.COL_CODE)
                if code == item.text():
                    print(f'{common.getCurDateTime()}_[{self.name}][receive_realdata][VI발동/해제][기존] 코드: {code}, 종목: {codename}, VI발동구분: {vigubun}, {type(vigubun)}, VI발동방향구분: {vipoint}, VI해제시각: {virelease}, VI적용구분: {vitype}')
                    item = self.caller.tableWidget.item(vi_index, self.caller.COL_HEJI_TIME)
                    item.setBackground(QtGui.QColor(200, 200, 0, 200))
                    self.caller.tableWidget.setItem(vi_index, self.caller.COL_HEJI_TIME, item)

                    item = QTableWidgetItem(sigapercent)
                    if sigapercent[0] == '+':
                        item.setForeground(QtGui.QColor(250, 50, 0, 250))
                        item.setBackground(QtGui.QColor(250, 0, 0, 25))
                    else:
                        item.setForeground(QtGui.QColor(0, 50, 250, 250))
                        item.setBackground(QtGui.QColor(0, 0, 250, 25))
                    self.caller.tableWidget.setItem(vi_index, self.caller.COL_SIGA_PERCENT, item)

                    item = QTableWidgetItem(dongjeokprice)
                    if int(dongjeokprice) > 0:
                        item.setForeground(QtGui.QColor(250, 50, 0, 250))
                        item.setBackground(QtGui.QColor(250, 0, 0, 25))
                    elif int(dongjeokprice) < 0:
                        item.setForeground(QtGui.QColor(0, 50, 250, 250))
                        item.setBackground(QtGui.QColor(0, 0, 250, 25))
                    self.caller.tableWidget.setItem(vi_index, self.caller.COL_PRICE_DONGJEOK, item)

                    item = QTableWidgetItem(jeongjeokprice)
                    if int(jeongjeokprice) > 0:
                        item.setForeground(QtGui.QColor(250, 50, 0, 250))
                        item.setBackground(QtGui.QColor(250, 0, 0, 25))
                    elif int(jeongjeokprice) < 0:
                        item.setForeground(QtGui.QColor(0, 50, 250, 250))
                        item.setBackground(QtGui.QColor(0, 0, 250, 25))
                    self.caller.tableWidget.setItem(vi_index, self.caller.COL_PRICE_JUNGJEOK, item)

                    self.caller.tableWidget.setItem(vi_index, self.caller.COL_GERRERAYNG, QTableWidgetItem(gererayng))
                    self.caller.tableWidget.setItem(vi_index, self.caller.COL_BALDONG_TIME, QTableWidgetItem(memetime))

                    item = QTableWidgetItem(virelease)
                    item.setForeground(QtGui.QColor(250, 50, 0, 250))
                    item.setBackground(QtGui.QColor(250, 0, 0, 25))
                    self.caller.tableWidget.setItem(vi_index, self.caller.COL_HEJI_TIME, item)

                    self.caller.tableWidget.setItem(vi_index, self.caller.COL_BALDONG_PRICE, QTableWidgetItem(baldongprice))
                    self.caller.tableWidget.setItem(vi_index, self.caller.COL_VI_COUNT, QTableWidgetItem(vibaldongcount))

    def stock_buy_more(self, code, quantity, screenno):
        data = self.kiwoom.SendOrder('BUY_RQ', str(screenno), self.account_num, 1, code, quantity, 0, '03', "")
        if data == 0:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_buy_more] 시장가 매수 호출 성공!', code, quantity)
        else:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_buy_more] 시장가 실패.. PASS - ' + str(data))

    # def stock_buy_more_ioc(self, code, quantity, screenno):
    #     data = self.kiwoom.SendOrder('BUY_RQ', str(screenno), self.account_num, 1, code, quantity, 0, '13', "")
    #     if data == 0:
    #         print(f'{common.getCurDateTime()}_[{self.name}][stock_buy_more] 시장가IOC 매수 호출 성공!', code, quantity)
    #     else:
    #         print(f'{common.getCurDateTime()}_[{self.name}][stock_buy_more] 실패.. PASS - ' + str(data))

    # def stock_buy_more_selfcost(self, code, quantity, cost, screenno):
    #     data = self.kiwoom.SendOrder('BUY_RQ', str(screenno), self.account_num, 1, code, quantity, cost, '00', "")
    #     if data == 0:
    #         print(f'{common.getCurDateTime()}_[{self.name}][stock_buy_more_selfcost] 매수 호출 성공!', code, quantity, cost)
    #     else:
    #         print(f'{common.getCurDateTime()}_[{self.name}][stock_buy_more_selfcost] 실패.. PASS - ' + str(data))

    def stock_sell_all(self, code, quantity, screenno):
        if self.caller.STOCK_REAL_BUY_STARTED:
            print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {code}, {quantity}주 전량 매도 접수')
            data = self.kiwoom.SendOrder('SELL_RQ', str(screenno), self.account_num, 2, code, quantity, 0, '03', "")
            if data == 0:
                print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_all] 매도 호출 성공!', code, quantity)
            else:
                print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_all] 실패.. PASS - ' + str(data))
        else:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_all][매도패스] STOCK_REAL_BUY_STARTED is not enable')

    def stock_sell_all_manual(self, code, quantity, screenno):
        print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {code}, {quantity}주 메뉴얼 전량 매도 접수')
        data = self.kiwoom.SendOrder('SELL_RQ', str(screenno), self.account_num, 2, code, quantity, 0, '03', "")
        if data == 0:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_all_manual] 메뉴얼 전량 매도 호출 성공!', code, quantity)
        else:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_all_manual] 메뉴얼 전량 매도 실패.. PASS - ' + str(data))

    def stock_cancel_all(self, code, quantity, screenno, orderno):
        print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {code}, {quantity}주 전량 취소 접수')
        # data = self.kiwoom.SendOrder('CANCEL_RQ', str(screenno), self.account_num, 3, code, quantity, 0, '00', "")
        # if data == 0:
        #     print(f'{common.getCurDateTime()}_[{self.name}][stock_cancel_all] 매수 취소 호출 성공!', code, quantity)
        # else:
        #     print(f'{common.getCurDateTime()}_[{self.name}][stock_cancel_all] 실패.. PASS - ' + str(data))
        data = self.kiwoom.SendOrder('CANCEL_RQ', str(screenno), self.account_num, 4, code, quantity, 0, '00', orderno)
        if data == 0:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_cancel_all] 전량 취소 호출 성공!', code, quantity)
        else:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_cancel_all] 전량 취소 실패.. PASS - ' + str(data))

    def stock_sell_single(self, code, quantity):
        if self.caller.STOCK_REAL_BUY_STARTED:
            if code == '090430': # 아모레 살려두기위한 장치, 임시
                pass
            else:
                print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {code}, {quantity}주 매도 접수')
                data = self.kiwoom.SendOrder('SELL_SINGLE_RQ', '9999', self.account_num, 2, code, quantity, 0, '03', "")
                if data == 0:
                    print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_single] 매도 호출 성공!', code, quantity)
                else:
                    print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_single] 실패.. PASS - ' + str(data))
        else:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_single][매도패스] STOCK_REAL_BUY_STARTED is not enable')

    def stock_sell_single_manual(self, code, quantity):
        print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {code}, {quantity}주 매뉴얼 매도 접수')
        data = self.kiwoom.SendOrder('SELL_SINGLE_RQ', '9999', self.account_num, 2, code, quantity, 0, '03', "")
        if data == 0:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_single_manual] 매뉴얼 매도 호출 성공!', code, quantity)
        else:
            print(f'{common.getCurDateTime()}_[{self.name}][stock_sell_single_manual] 매뉴얼 매도 호출 실패.. PASS - ' + str(data))

    def new_stock_buy(self, self_name, codename, code, quantity):
        if self.caller.STOCK_REAL_BUY_STARTED is False:
            print(f"{common.getCurDateTime()}_[{self_name}][매수패스] stock_buy is not enabled, {codename}, {code}, {quantity}")
            print(f"{common.getCurDateTime()}_[{self_name}][매수패스] stock_buy is not enabled, {codename}, {code}, {quantity}", file=self.caller.viLogFile)
            return
        elif code == '-':
            print(f"{common.getCurDateTime()}_[{self_name}][매수패스] no code or name, {codename}, {code}")
            print(f"{common.getCurDateTime()}_[{self_name}][매수패스] no code or name, {codename}, {code}", file=self.caller.viLogFile)
            return
        else:
            try:
                print(f"{common.getCurDateTime()}_[{self_name}][키움매수접수] 시도, account_num: {self.account_num}, {codename}, {code}, {quantity}")
                print(f"{common.getCurDateTime()}_[{self_name}][키움매수접수] 시도, account_num: {self.account_num}, {codename}, {code}, {quantity}", file=self.caller.viLogFile)
                if self.account_num is not None:
                    print(f"{common.getCurDateTime()}_[키움매수접수] stock_buy() - 종목: " + codename + ", 코드: " + code)
                    #######################################################
                    print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {code}, {quantity}주 매수 접수, 1')
                    data = self.kiwoom.SendOrder('BUY_RQ', str(self.caller.buy_sell_screen_no), self.account_num, 1, code, quantity, 0, '03', "")
                    if data == -308:
                        print(f'{common.getCurDateTime()}_[키움매수접수]|실패|주문전송 과부하, 1초 후 재시도|{codename}|{code}|{quantity}', file=self.caller.viLogFile)
                        print(f'{common.getCurDateTime()}_[키움매수접수]|실패|주문전송 과부하, 1초 후 재시도|{codename}|{code}|{quantity}')
                        time.sleep(0.3)
                        print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {code}, {quantity}주 매수 접수, 2')
                        data = self.kiwoom.SendOrder('BUY_RQ', str(self.caller.buy_sell_screen_no), self.account_num, 1, code, quantity, 0, '03', "")
                        if data == 0:
                            print(f'{common.getCurDateTime()}_[키움매수접수]|성공|PASS|{codename}|{code}|{quantity}', file=self.caller.viLogFile)
                            print(f'{common.getCurDateTime()}_[키움매수접수]|성공|PASS|{codename}|{code}|{quantity}')
                            # self.caller.insertToBuyTable(common.getCurPcTime(), '-', '-', codename, code, quantity, 0, broadcast + ':' + customword, '접수')
                        else:
                            print(f'{common.getCurDateTime()}_[키움매수접수]|실패|PASS|{codename}|{code}|{quantity}', file=self.caller.viLogFile)
                            print(f'{common.getCurDateTime()}_[키움매수접수]|실패|PASS|{codename}|{code}|{quantity}')
                    if data == 0:
                        print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {code}, {quantity}주 매수 접수 성공')
                        print(f'{common.getCurDateTime()}_[키움매수접수]|성공|PASS|{codename}|{code}|{quantity}', file=self.caller.viLogFile)
                        print(f'{common.getCurDateTime()}_[키움매수접수]|성공|PASS|{codename}|{code}|{quantity}')
            except Exception as e:
                print(f'{common.getCurDateTime()}_[키움매수접수]|오류|{e}|{codename}|{code}|{quantity}', file=self.caller.viLogFile)
                print(f'{common.getCurDateTime()}_[키움매수접수]|오류|{e}|{codename}|{code}|{quantity}')
                common.error_popup("매수 호출 오류", str(e))

    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
           self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_no, code_list, fid_list, real_type)

    def DisConnectRealData(self, screen_no):
        self.kiwoom.dynamicCall("DisConnectRealData(QString)", screen_no)

    def GetCommRealData(self, code, fid):
        data = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return data

    def checkAlreadyBought(self, codename, code):
        isfirstbuy = True
        codeandcodename = codename + '(' + code + ')'

        for row in range(self.caller.tableWidget.rowCount()):
            item = self.caller.tableWidget.item(row, self.caller.COL_CODE).text()
            # print('[checkAlreadyBought] Looking for the row', str(row), codeandcodename,  item)
            if codeandcodename == item:
                isfirstbuy = False
                print(f'{common.getCurDateTime()}_[{self.name}][checkAlreadyBought] Already in buy list, pass', codeandcodename)
                break
        return isfirstbuy

    def get_chejan_data(self, fid):
        ret = self.kiwoom.dynamicCall("GetChejanData(int)", fid)
        return ret

    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        # 주문 체결 통보
        if gubun == '0':
            status = self.get_chejan_data(913)              # 주문상태(접수,확인,체결)
            orderno = self.get_chejan_data(9203)            # 주문번호
            ordernoori = self.get_chejan_data(904)          # 원주문번호
            notyettrans = self.get_chejan_data(902)         # 미체결수량
            code = self.get_chejan_data(9001)               # 종목코드
            codename = self.get_chejan_data(302)            # 종목명
            quantity = self.get_chejan_data(900)            # 주문수량
            ordercost = self.get_chejan_data(901)           # 주문가격
            curtime = self.get_chejan_data(908)             # 주문/체결시간(HHMMSSMS)
            contractcost = self.get_chejan_data(910)        # 체결가
            contractquantity = self.get_chejan_data(911)    # 체결량
            curcost = self.get_chejan_data(10)              # 현재가,체결가,실시간종가
            sellorbuy = self.get_chejan_data(907)           # 매도수구분 1매도 2매수

            newcodename = codename.strip()
            newcode = code[1:]
            timewithcolumn = curtime[:2] + ':' + curtime[2:4] + ':' + curtime[4: ]
            print('[_receive_chejan_data]', gubun, timewithcolumn, status, str(orderno), newcode, newcodename, str(quantity), str(contractcost), str(curcost))
            if status == '접수':
                # if sellorbuy == '2':
                    # 실시간 등록 (접수 시점으로 이동) ##
                    # print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {newcode} 1주 접수 완료, 실시간 등록')
                    # self.addRealTimeRegCode(newcode)
                    # self.startRealtimeMonitor()
                    #######################################################
                print(f'{common.getCurDateTime()}_[{self.name}][_receive_chejan_data] 접수 완료(1: 매도, 2: 매수)', sellorbuy, timewithcolumn, '코드', newcode, '종목', codename.strip(), '체결량', contractquantity, '주문가', ordercost, '체결가', contractcost, '미체결량', notyettrans)
                # column_headers = ['요청시간', '체결시간', '주문번호', '코드', '종목', '수량', '미체결수량', '매수가', '현재가', '평가손익', '수익률(%)', '뉴스제공사', '상태'
                self.caller.MYSTOCK.add_or_update_stock(sellorbuy, timewithcolumn, '-', orderno, newcode, newcodename, int(quantity), 0, int(notyettrans), ordercost, curcost, 0, '-', '-', '접수')
                # self.caller.modifyBuyTable(status, orderno, timewithcolumn, curcost, newcode, newcodename)
            elif status == '체결':
                print(f'{common.getCurDateTime()}_[{self.name}][_receive_chejan_data] 체결 완료(1: 매도, 2: 매수)', sellorbuy, timewithcolumn, '코드', newcode, '종목', codename.strip(), '체결량', contractquantity, '주문가', ordercost, '체결가', contractcost, '미체결량', notyettrans)
                if int(notyettrans) > 0:
                    # self.caller.modifyBuyTable(status, orderno, timewithcolumn, curcost, newcode, newcodename)
                    self.caller.MYSTOCK.add_or_update_stock(sellorbuy, '-', timewithcolumn, orderno, newcode, newcodename, int(quantity), 0, int(notyettrans), contractcost, curcost, 0, '-', '-', '체결중')
                else:
                    # self.caller.modifyBuyTable(status, orderno, timewithcolumn, curcost, newcode, newcodename)
                    self.caller.MYSTOCK.add_or_update_stock(sellorbuy, '-', timewithcolumn, orderno, newcode, newcodename, int(quantity), 0, int(notyettrans), contractcost, curcost, 0, '-', '-', '체결완료')
                    # 처음 매수 후, 제한 수량까지 매수하는 부분 제거
                    # if sellorbuy == '2':
                    #     ## 실시간 등록 (매수 완료 시점이 아닌, 매수 호출 시점으로 이동 함) ##
                    #     # print(f'{common.getCurDateTime()}_[{self.name}] ------------------------------------------------------ {newcode} 1주 체결 완료, 실시간 등록')
                    #     # self.addRealTimeRegCode(newcode)
                    #     # self.startRealtimeMonitor()
                    #     ########################################################
                    #     for stock in self.caller.MYSTOCK.my_stocks:
                    #         if stock.stock_code == newcode:
                    #             # 첫 매수일 때,
                    #             if stock.firstbuyorder_done == False:
                    #                 stock.firstbuy_price = contractcost
                    #                 stock.firstbuytime = time.time()
                    #                 stock.firstbuyorder_done = True
                    #                 print(f'{common.getCurDateTime()}_[{self.name}][_receive_chejan_data] 최초 매수 완료, code: {stock.stock_code}, price: {stock.firstbuy_price}')
                    #                 if self.caller.medohoga == 1:
                    #                     # 체결 후에 시장가IOC로 제한 수량 까지 추가 구매 요청
                    #                     to_buy = trunc(int(self.caller.BUY_MINIMUM_COST_WON / int(contractcost))) - 1
                    #                     if to_buy > 0:
                    #                         print(f'{common.getCurDateTime()}_[{self.name}][_receive_chejan_data] 시장가IOC로 추가 매수 호출, {to_buy}주, 코드: {newcode}')
                    #                         print(f'{common.getCurDateTime()}_[{self.name}][_receive_chejan_data] 시장가IOC로 추가 매수 호출, {to_buy}주, 코드: {newcode}', file=self.caller.viLogFile)
                    #                         # self.caller.KIWOOM.stock_buy_more(stock_code, to_buy, "9999")
                    #                         self.caller.KIWOOM.stock_buy_more_ioc(newcode, to_buy, "9999")
                    #                     else:
                    #                         print(f'{common.getCurDateTime()}_[{self.name}][_receive_chejan_data] 추가 매수 금액 충족, 패스')
                    #
                    #                     stock.buymore_done = True
                    #             break
        # 국내주식 잔고통보
        elif gubun == '1':
            codename = self.get_chejan_data(302).strip()# 종목명
            totalcount = self.get_chejan_data(930)      # 보유수량
            avgcost = self.get_chejan_data(931)         # 매입단가
            totalcost = self.get_chejan_data(932)       # 총매입가
            availcount = self.get_chejan_data(933)      # 주문가능수량
            remaincost = self.get_chejan_data(951)      # 예수금
            standardcost = self.get_chejan_data(307)    # 기준가
            profitpercent = self.get_chejan_data(8019)  # 손익률
            print(f'{common.getCurDateTime()}_[{self.name}][_receive_chejan_data] 잔고통보, {gubun}, 종목명:{codename}, 보유수량:{totalcount}, 매입단가:{avgcost}, 총매입가:{totalcost}, 주문가능수량:{availcount}, 예수금:{remaincost}, 기준가:{standardcost}, 손익률:{profitpercent}')
            self.caller.MYSTOCK.updateBalanceToTable(codename, totalcount, avgcost)
            pass
        return

    def get_account_stock(self, sPrevNext="0"):
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호", "")
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "조회구분", "1")
        self.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "계좌상세요청", "opw00004", sPrevNext, self.screenNo_account)
        self.account_event_loop = QEventLoop()
        self.account_event_loop.exec_()

    def get_account_evaluation_balance(self, nPrevNext=0):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", nPrevNext, self.screenNo_account)
        self.account_event_loop = QEventLoop()
        self.account_event_loop.exec_()

    def get_sichong(self, code):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식기본정보요청", "opt10001", 0, self.screenNo_account)

    def request_hoga(self, code):
        # print(f'{common.getCurDateTime()}_[{self.name}][request_hoga] code:{code}, len: {len(code)} 1')
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        # print(f'{common.getCurDateTime()}_[{self.name}][request_hoga] code:{code}, len: {len(code)} 2')
        res = self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식호가요청", "opt10004", 0, self.screenNo_hoga)
        # print(f'{common.getCurDateTime()}_[{self.name}][request_hoga] res: {common.error_code_list(res)}, code:{code}, len: {len(code)}')
        return res

    def updateHogaByCode(self, code, value):
        self.caller.kospi_dic_hoga_by_code[code] = value

    def request_vi(self):
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "시장구분", "000")  # 000 전체 001 코스피 101 코스닥
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "장전구분", "1")  # 0 전체 1 정규시장 2 시간외단일가
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "종목코드", "")  # 전문조회할 종목코드, 공백 시 시장구분으로 전체종목조회
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "발동구분", "0")  # 0 전체 1 정적 2 동적 3 정적+동적
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "제외종목", "110010011")  # 조회포함(0), 조회제외(1), 전 종목 포함 시 9개 000000000, 순서: 우선주,관리종목,투자경고/위험,투자주의,환기종목,단기과열종목,증거금100%,ETF,ETN
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "거래량구분", "0")  # 0 OFF 1 ON
        # self.kiwoom.dynamicCall("SetInputValue(String, String)", "최소거래량", "0") # 1 = 1주이상 (공백허용)
        # self.kiwoom.dynamicCall("SetInputValue(String, String)", "최대거래량", "0") # 1 = 1주이하 (공백허용)
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "거래대금구분", "1")  # 0 OFF 1 ON
        # self.kiwoom.dynamicCall("SetInputValue(String, String)", "최소거래대금", "0") # 1 = 1백만원 이상 (공백허용)
        # self.kiwoom.dynamicCall("SetInputValue(String, String)", "최대거래대금", "0") # 1 - 1백만원 이하 (공백허용)
        self.kiwoom.dynamicCall("SetInputValue(String, String)", "발동방향", "1")  # 0 전체 1 상승 2 하락
        self.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "VI발동", "opt10054", 0, self.screenNo_vi)
        # self.CommRqData("VI발동", "opt10054", 0, self.screenNo_vi)

    def receive_trdata(self, scrno, sRQName, sTrCode, recordname, sPrevNext):
        # screen 번호, 요청시이름, tr코드, 사용x, 다음페이지여부
        # if sRQName == "VI발동":
        #     self.viReceived(sTrCode, recordname);

        if sRQName == "계좌상세요청":
            pass
            # nCnt = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            # print('[receive_trdata]', sRQName, nCnt)
            # # OPW00004 = 종목코드, 종목명, 보유수량, 평균단가, 현재가, 평가금액, 손익금액, 손익률
            # for loop in range(nCnt):
            #     stock_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, loop, "종목코드")
            #     stock_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, loop, "종목명")
            #     stock_count = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, loop, "보유수량")
            #     stock_avg = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, loop, "평균단가")
            #     print(f'[계좌상세요청] 종목코드: {stock_code} + 종목명: {stock_name} + 보유수량: {stock_count} + 평균단가: {stock_avg}')

        elif sRQName == "주식기본정보요청":
            code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            sichong = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "시가총액")

            print(f'{common.getCurDateTime()}_[{self.name}][시총][주식기본정보요청] {code.strip()}, {sichong.strip()}')

        elif sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
            self.total_buy_money = int(total_buy_money)
            total_evaluation_money = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액")
            self.total_evaluation_money = int(total_evaluation_money)
            total_evaluation_profit_and_loss_money = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액")
            self.total_evaluation_profit_and_loss_money = int(total_evaluation_profit_and_loss_money)
            total_yield = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
            self.total_yield = float(total_yield)

            cnt = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print(f'{common.getCurDateTime()}_[{self.name}][계좌평가잔고내역요청] 총종목 수: {cnt}, 총매입금액: {total_buy_money}, 총평가금액: {total_evaluation_money}, 총평가손익금액: {total_evaluation_profit_and_loss_money}, 총수익률(%): {total_yield}')

            # realtime stop
            self.stopRealtimeMonitor('', True)
            self.clearRealTimeRegCode()
            for i in range(cnt):
                stock_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                stock_code = stock_code.strip()[1:]

                self.addRealTimeRegCode(stock_code)

                stock_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_name = stock_name.strip()  # 필요 없는 공백 제거

                stock_evaluation_profit_and_loss = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "평가손익")
                stock_evaluation_profit_and_loss = int(stock_evaluation_profit_and_loss)

                stock_yield = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                stock_yield = float(stock_yield) / 100.0

                stock_buy_money = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                stock_buy_money = int(stock_buy_money)

                stock_quantity = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                stock_quantity = int(stock_quantity)

                stock_trade_quantity = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")
                stock_trade_quantity = int(stock_trade_quantity)

                stock_present_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                stock_present_price = int(stock_present_price)

                print(f'{common.getCurDateTime()}_[{self.name}][계좌평가잔고내역요청] 종목번호: {stock_code} 종목명: {stock_name} 평가손익: {stock_evaluation_profit_and_loss} 수익률(%): {stock_yield} 매입가: {stock_buy_money} 보유수량: {stock_quantity} 매매가능수량: {stock_trade_quantity} 현재가: {stock_present_price}')

                #add_stock(self, req_time, res_time, order_no, stock_code, stock_name, stock_count, stock_yet_count, buy_cost, cur_cost, profit, profit_per, broker, status):
                self.caller.MYSTOCK.add_stock_from_account(stock_code, stock_name, stock_quantity, stock_buy_money, stock_present_price, stock_evaluation_profit_and_loss, stock_yield)
                # self.caller.insertAccountStockToTable(stock_code, stock_name, stock_evaluation_profit_and_loss, stock_yield, stock_buy_money, stock_quantity, stock_present_price)
            if sPrevNext == "2":
                self.get_account_evaluation_balance("2")
            else:
                self.cancel_screen_number(self.screenNo_account)
                # realtime start
                self.startRealtimeMonitor()

            # self.caller.MYSTOCK.show_all_stock()
            self.account_event_loop.exit()
            self.caller.tableWidgetSyncBtn.setEnabled(True)

    def cancel_screen_number(self, sScrNo):
        self.kiwoom.dynamicCall("DisconnectScreenNoData(QString)", sScrNo)