import ctypes
import multiprocessing
import pickle
import sys
import threading
import warnings
from queue import Queue

from PyQt5.QtWidgets import QPushButton, QTabWidget, QWidget, QGridLayout, QGroupBox, QLabel, QComboBox, QMainWindow, \
    QHBoxLayout, QVBoxLayout, QListView, QAbstractItemView, QTimeEdit, QCheckBox, QTableWidget, QHeaderView, \
    QTableWidgetItem, QListWidget, QListWidgetItem, QDialog, QApplication, QDoubleSpinBox
from playsound import playsound

from mystock import MyStock

# import news_data_queue
# from news_item import NewsItemClass

warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

from PyQt5 import QtCore, QtWidgets
from pathlib import Path
from kiwoom import *

enable_stock_kiwoom = True

class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.STOCK_REAL_BUY_STARTED = False

        self.NAME = "StockVI"
        self.BUY_START_PERCENT = 1
        self.SELL_LOW_CUTLINE_PERCENT = -1
        self.SELL_HIGH_CUTLINE_PERCENT = 2
        self.SELL_CUTLINE_TIMESEC = 300
        self.BUY_MINIMUM_COST_MANWON = 10
        self.BUY_MIN_GERERYANG = 0
        self.BUY_PROFIT_PERCENT = 300
        self.SEC_WAIT_SELL_AFTER_BUY = 30
        # self.BUY_MINIMUM_COST_WON = self.BUY_MINIMUM_COST_MANWON * 10000

        # self.GLOBAL_LIST = []

        self.openOptionFile()
        self.MYSTOCK = MyStock(self)

        timestr = time.strftime("%Y%m%d_%H%M%S")
        self.viLogFile = open('log_' + timestr + '.txt', 'w', encoding='UTF-8')
        self.autoScrollEnabeld = True
        self.playSound = True
        self.waitSound = 0
        self.buy_sell_screen_no = 7000

        self.listWatchData = []
        self.news_matching = []
        self.news_filterword = []
        self.news_filterstock = []
        self.news_matching_custom = {}

        if ctypes.windll.shell32.IsUserAnAdmin():
            print(f'{common.getCurDateTime()}_[{self.NAME}] 정상: 관리자권한으로 실행된 프로세스입니다.')
        else:
            common.error_popup("관리자권한", "마우스 우클릭 -> 관리자 권한으로 실행 해주세요.")
            exit()

        ###### UI Setting ######
        self.setupUI()
        ########################

        if enable_stock_kiwoom:
            self.KIWOOM = KiwoomAPI(self)
            self.KIWOOM.kiwoomInit()
            self.KIWOOM.getAccountInfo(self.kiwoom_status)
            self.saveStockNameInfoFile(self.KIWOOM.getStockInfo())
            self.openStockNameInfoFile()
            self.saveStockCodeInfoFile(self.KIWOOM.getStockInfo2())
            self.openStockCodeInfoFile()
            self.KIWOOM.request_vi()

        # self.trd = news_data_queue.NewsDataQueue('VI', self)
        # self.trd.daemon = True
        # self.trd.start()
        # self.trd.sendKiwoomRequest.connect(self.sendKiwoomRequest)

# threading.Timer(3.7, self.callHogaGetTimer).start()

    @pyqtSlot(str, str)
    def sendKiwoomRequest(self, code, codename):
        if self.STOCK_REAL_BUY_STARTED and code != '-':
            print(f'{common.getCurDateTime()}_[{self.NAME}] {code} - {codename} 호가 요청 등록')
            self.code_to_buy = code
            self.name_to_buy = codename
            self.KIWOOM.request_hoga(code)
            self.KIWOOM.addRealTimeRegCode(code)
            self.KIWOOM.startRealtimeMonitor()
        else:
            print(f'{common.getCurDateTime()}_[{self.NAME}] {code} 호가 요청 등록 실패 - STOCK_REAL_BUY_STARTED is {self.STOCK_REAL_BUY_STARTED}')

    def setupUI(self):
        # Main Window
        self.setWindowTitle("StockVI")
        self.setGeometry(50, 50, 1550, 800)
        self.setCentralWidget(self.mainLayout())

    def curTime(self):
        # now = time.localtime()
        # # print"%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        # return "%02d:%02d:%02d" % (now.tm_hour, now.tm_min, now.tm_sec)
        time = QTime.currentTime()
        print(time.toString('hh.mm.ss.zzz'))

    def mainLayout(self):
        widget = QWidget(self)
        grid = QGridLayout(widget)
        grid.addWidget(self.connectionGroup(),      0, 0)# row, column, rowspan, columnspan
        grid.addWidget(self.startstopGroup(),       0, 1)
        grid.addWidget(self.tempGroup(),            0, 2)
        grid.addWidget(self.tempGroup(),            0, 3)
        grid.addWidget(self.tableGroup(),           1, 0, 1, 4)
        grid.addWidget(self.buytab2(),              2, 0, 1, 4)
        # grid.addWidget(self.buyListGroup(),         2, 0, 1, 4)


        # grid.addWidget(self.connectionGroup(),      12, 0, 2, 1)
        # grid.addWidget(self.startstopGroup(),       12, 1, 1, 1)
        # grid.addWidget(self.timeGroup(),            13, 1, 1, 1)
        # grid.addWidget(self.hogaGroup(),            12, 2, 2, 2)
        # grid.addWidget(self.newsListGroup(),        0, 0, 8, 6)
        # grid.addWidget(self.buyListGroup(),         8, 0, 4, 6)
        tab = QWidget()
        tab.setLayout(grid)
        return tab

    def connectionGroup(self):
        self.kiwoom_status = QLabel(self)
        self.kiwoom_status.setEnabled(False)
        self.kiwoom_status.setText('키움 - 로그인 필요')
        self.kiwoom_status.setAlignment(Qt.AlignCenter);
        self.kiwoom_status.setStyleSheet('color:rgb(%s,%s,%s)' % (255, 100, 100))

        self.kiwoom_acc = QComboBox(self)
        self.kiwoom_acc.activated[str].connect(self.kiwoom_acc_selected)

        self.soundBtn = QPushButton('소리 켜짐')
        self.soundBtn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 100, 250, 255, 255, 255))
        self.soundBtn.clicked.connect(self.soundBtnClicked)

        self.auto_scroll_checkbox = QCheckBox('자동 스크롤', self)
        self.auto_scroll_checkbox.toggle()
        self.auto_scroll_checkbox.stateChanged.connect(self.autoScrollStateChange)

        self.tableWidgetSyncBtn = QPushButton('계좌 동기화')
        self.tableWidgetSyncBtn.clicked.connect(self.tableWidgetSyncBtnClicked)
        self.tableWidgetSyncBtn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 100, 250, 255, 255, 255))

        self.tableWidgetPasswordBtn = QPushButton('계좌 비번')
        self.tableWidgetPasswordBtn.clicked.connect(self.tableWidgetPasswordBtnClicked)
        self.tableWidgetPasswordBtn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 100, 250, 255, 255, 255))

        hbox = QHBoxLayout()
        hbox.addWidget(self.auto_scroll_checkbox)
        hbox.addWidget(self.soundBtn)
        hbox.addWidget(self.tableWidgetSyncBtn)
        hbox.addWidget(self.tableWidgetPasswordBtn)

        vbox = QVBoxLayout()
        vbox.addWidget(self.kiwoom_status)
        vbox.addWidget(self.kiwoom_acc)
        vbox.addLayout(hbox)

        groupbox = QGroupBox('계좌정보')
        groupbox.setCheckable(False)
        groupbox.setMaximumHeight(150)
        groupbox.setLayout(vbox)
        return groupbox

    def startstopGroup(self):
        self.btnServiceStart = QPushButton('시작')
        self.btnServiceStart.clicked.connect(self.btnServiceStartClicked)
        self.btnServiceStart.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (150, 150, 150, 255, 255, 255))

        self.btnServiceStop = QPushButton('중지')
        self.btnServiceStop.clicked.connect(self.btnServiceStopClicked)
        self.btnServiceStop.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (150, 150, 150, 255, 255, 255))
        self.btnServiceStop.setEnabled(False)

        vbox = QVBoxLayout()
        vbox.addWidget(self.btnServiceStart)
        vbox.addWidget(self.btnServiceStop)

        groupbox = QGroupBox('시작/중지')
        groupbox.setCheckable(False)
        groupbox.setMaximumHeight(150)
        groupbox.setLayout(vbox)
        return groupbox

    def tempGroup(self):
        tempLabel = QLabel('-')
        vbox = QVBoxLayout()
        vbox.addWidget(tempLabel)
        groupbox = QGroupBox('-')
        groupbox.setCheckable(False)
        groupbox.setMaximumHeight(150)
        groupbox.setLayout(vbox)
        return groupbox

    # def test_mesu_clicked(self):
    #     new_news = NewsItemClass(time.time(), self.test_mesu_cost.toPlainText(), self.kospi_dic_by_code_main.get(self.test_mesu_cost.toPlainText(), '-'), '-', '-', '-','-', '-', '-','-', '-',1, '', False, '',False)
    #     new_news.n_BUY_DONE = True
    #     self.GLOBAL_LIST.insert(0, new_news)
    #     self.sendKiwoomRequest(new_news.n_code, self.kospi_dic_by_code_main.get(new_news.n_code))

    def kiwoom_acc_selected(self, acc_num):
        self.KIWOOM.setCurAccountNum(acc_num)
        self.tableWidgetSyncBtnClicked()

    def setColortoRow(self, row_index, color):
        for j in range(self.tableWidget.columnCount()):
            self.tableWidget.item(row_index, j).setBackground(color)
        # self.tableWidget.resizeRowsToContents()
        # QApplication.processEvents()
        # QCoreApplication.processEvents()

    def setColorEmptyRow(self, row_index, color):
        for j in range(self.tableWidget.columnCount()):
            try:
                self.tableWidget.item(row_index, j).setBackground(color)
            except:
                pass

    def PlaySoundEffect(self, src):
        try:
            if self.playSound:
                if (time.time() - self.waitSound) > 1:
                    self.waitSound = time.time()
                    soundThread = threading.Thread(target=lambda: playsound(src))
                    soundThread.start()
        except Exception as e:
            print(f'{common.getCurDateTime()}_[{self.NAME}] [PlaySoundEffect] Exception:', e)

    def saveStockNameInfoFile(self, temp):
        with open('stock_name_info.txt', 'wb') as fp:
            pickle.dump(temp, fp)

    def saveStockCodeInfoFile(self, temp):
        with open('stock_code_info.txt', 'wb') as fp:
            pickle.dump(temp, fp)

    def openStockNameInfoFile(self):
        openFile = Path('stock_name_info.txt')
        if openFile.is_file() is True:
            with open(openFile, 'rb') as fp:
                self.kospi_dic_by_name_main = pickle.load(fp)

    def openStockCodeInfoFile(self):
        openFile = Path('stock_code_info.txt')
        if openFile.is_file() is True:
            with open(openFile, 'rb') as fp:
                self.kospi_dic_by_code_main = pickle.load(fp)
            print(f'{common.getCurDateTime()}_[openStockCodeInfoFile] kospi_dic_by_code_main, 종목 수: {len(self.kospi_dic_by_code_main)}')

    def saveOptionFile(self):
        f = open('option.txt', "w", encoding="UTF-8")
        print(f'{common.getCurDateTime()}_[{self.NAME}][saveOptionFile] {self.SELL_LOW_CUTLINE_PERCENT}')
        print(f'{common.getCurDateTime()}_[{self.NAME}][saveOptionFile] {self.SELL_HIGH_CUTLINE_PERCENT}')
        print(f'{common.getCurDateTime()}_[{self.NAME}][saveOptionFile] {self.SELL_CUTLINE_TIMESEC}')
        print(f'{common.getCurDateTime()}_[{self.NAME}][saveOptionFile] {self.BUY_MINIMUM_COST_MANWON}')
        print(f'{common.getCurDateTime()}_[{self.NAME}][saveOptionFile] {self.BUY_MIN_GERERYANG}')
        print(f'{common.getCurDateTime()}_[{self.NAME}][saveOptionFile] {self.BUY_PROFIT_PERCENT}')
        print(f'{common.getCurDateTime()}_[{self.NAME}][saveOptionFile] {self.mesuvi_type}')
        print(f'{common.getCurDateTime()}_[{self.NAME}][saveOptionFile] {self.SEC_WAIT_SELL_AFTER_BUY}')
        print(f'{common.getCurDateTime()}_[{self.NAME}][saveOptionFile] {self.BUY_START_PERCENT}')
        f.write(f'{self.SELL_LOW_CUTLINE_PERCENT}\n')
        f.write(f'{self.SELL_HIGH_CUTLINE_PERCENT}\n')
        f.write(f'{self.SELL_CUTLINE_TIMESEC}\n')
        f.write(f'{self.BUY_MINIMUM_COST_MANWON}\n')
        f.write(f'{self.BUY_MIN_GERERYANG}\n')
        f.write(f'{self.BUY_PROFIT_PERCENT}\n')
        f.write(f'{self.mesuvi_type}\n')
        f.write(f'{self.SEC_WAIT_SELL_AFTER_BUY}\n')
        f.write(f'{self.BUY_START_PERCENT}\n')
        f.close()

    def openOptionFile(self):
        openFile = Path('option.txt')
        openFile.touch(exist_ok=True)
        f = open(openFile, "r", encoding="UTF-8")
        lines = f.readlines()
        for idx, line in enumerate(lines):
            nline = line.split('\n')[0]
            if idx == 0:
                self.SELL_LOW_CUTLINE_PERCENT = float(nline)
            elif idx == 1:
                self.SELL_HIGH_CUTLINE_PERCENT = float(nline)
            elif idx == 2:
                self.SELL_CUTLINE_TIMESEC = int(nline)
            elif idx == 3:
                self.BUY_MINIMUM_COST_MANWON = int(nline)
            elif idx == 4:
                self.BUY_MIN_GERERYANG = int(nline)
            elif idx == 5:
                self.BUY_PROFIT_PERCENT = int(nline)
            elif idx == 6:
                self.mesuvi_type = int(nline)
            elif idx == 7:
                self.SEC_WAIT_SELL_AFTER_BUY = int(nline)
            elif idx == 8:
                self.BUY_START_PERCENT = float(nline)
        f.close()

    def btnServiceStartClicked(self):
        if self.STOCK_REAL_BUY_STARTED is False:
            self.STOCK_REAL_BUY_STARTED = True
            self.btnServiceStart.setText('실행 중')
            self.btnServiceStart.setEnabled(False)
            self.btnServiceStart.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (250, 100, 0, 255, 255, 255))
            self.btnServiceStop.setEnabled(True)
            self.btnServiceStop.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (50, 50, 0, 255, 255, 255))

    def btnServiceStopClicked(self):
        if self.STOCK_REAL_BUY_STARTED:
            self.STOCK_REAL_BUY_STARTED = False
            self.btnServiceStart.setText('시작')
            self.btnServiceStart.setEnabled(True)
            self.btnServiceStart.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 100, 250, 255, 255, 255))
            self.btnServiceStop.setEnabled(False)
            self.btnServiceStop.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (150, 150, 150, 255, 255, 255))

    def dspinboxValueChange(self):
        self.news_refresh_time[0] = float(self.dspinbox.value())
        print(f'{common.getCurDateTime()}_[{self.NAME}][dspinboxValueChange] news_refresh_time: {self.news_refresh_time[0]}')

    def hspinboxValueChange(self):
        self.hoga_timer_interval = self.hspinbox.value()
        self.hoga_timer.setInterval(int(self.hoga_timer_interval * 1000))
        print(f'{common.getCurDateTime()}_[{self.NAME}][hspinboxValueChange] hoga_refresh_time: {int(self.hoga_timer_interval * 1000)}')

    def autoScrollStateChange(self, state):
        if state == Qt.Checked:
            self.auto_scroll_enabeld = True
            # self.tableWidget.setDisabled(True)
            # self.tableWidget2.setDisabled(True)
        else:
            self.auto_scroll_enabeld = False
            # self.tableWidget.setDisabled(False)
            # self.tableWidget2.setDisabled(False)
        print(f'{common.getCurDateTime()}_[{self.NAME}][autoScrollStateChange] state change: {state}, self.auto_scroll_enabeld: {self.auto_scroll_enabeld}')

    def tableGroup(self):
        # self.newsgroupbox = QGroupBox('뉴스')
        # self.newsgroupbox.setFlat(True)
        # self.newsgroupbox.setStyleSheet("QGroupBox{padding-top:15px; margin-top:-15px}")
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setMinimumHeight(200)
        self.tableWidget.setColumnCount(25)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tableWidget.verticalHeader().setDefaultSectionSize(12)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.tableWidget.setDisabled(True)
        # self.tableWidget.setStyleSheet('disabled{ background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)}' % (255, 0, 0, 255, 0, 0))
        # column_headers = ['시간', '코드', '종목명', '보고서', '영업이익', '영업이익-1Y', '증감(%)'] #, '매출액', '매출액-1Y', '증감(%)', '-1Y당기순이익', '당기순이익', '증감(%)']
        column_headers = ['코드', '종목명', '시가대비\n등락률', '기준가격\n동적VI', '기준가격\n정적VI', '거래량', '발동', '해지', '발동가격', '호가',
                          '횟수', '주문번호', '수량', '미체결', '매수가', '매도가', '현재가', '평가손익', '수익률', '상태', '금액(만)', '매수', '매도', '매도', '오토']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)
        self.tableWidget.verticalHeader().setVisible(True)
        #self.tableWidget.resizeColumnsToContents()
        #self.tableWidget.resizeRowsToContents()

        self.COL_CODE = 0
        self.COL_NAME = 1
        self.COL_SIGA_PERCENT = 2
        self.COL_PRICE_DONGJEOK = 3
        self.COL_PRICE_JUNGJEOK = 4
        self.COL_GERRERAYNG = 5
        self.COL_BALDONG_TIME = 6
        self.COL_HEJI_TIME = 7
        self.COL_BALDONG_PRICE = 8
        self.COL_HOGA = 9
        self.COL_VI_COUNT = 10
        self.COL_ORDERNUM = 11
        self.COL_COUNT_BOUGHT = 12
        self.COL_COUNT_NOTYET = 13
        self.COL_BUY_PRICE = 14
        self.COL_SELL_PRICE = 15
        self.COL_CUR_PRICE = 16
        self.COL_PROFIT_PRICE = 17
        self.COL_PROFIT_PERCENT = 18
        self.COL_STATUS = 19
        self.COL_WON_TO_BUY = 20
        self.COL_BTN_MESU = 21
        self.COL_BTN_MEDO30 = 22
        self.COL_BTN_MEDO100 = 23
        self.COL_BTN_AUTO = 24

        delegate = AlignDelegate(self.tableWidget)
        self.tableWidget.setItemDelegateForColumn(self.COL_CODE, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_NAME, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_SIGA_PERCENT, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_PRICE_DONGJEOK, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_PRICE_JUNGJEOK, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_GERRERAYNG, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_BALDONG_TIME, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_HEJI_TIME, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_BALDONG_PRICE, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_HOGA, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_VI_COUNT, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_ORDERNUM, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_COUNT_BOUGHT, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_COUNT_NOTYET, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_BUY_PRICE, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_SELL_PRICE, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_CUR_PRICE, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_PROFIT_PRICE, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_PROFIT_PERCENT, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_STATUS, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_WON_TO_BUY, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_BTN_MESU, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_BTN_MEDO30, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_BTN_MEDO100, delegate)
        self.tableWidget.setItemDelegateForColumn(self.COL_BTN_AUTO, delegate)
        self.tableWidget.setColumnWidth(self.COL_CODE, 50)
        self.tableWidget.setColumnWidth(self.COL_NAME, 100)
        self.tableWidget.setColumnWidth(self.COL_SIGA_PERCENT, 60)
        self.tableWidget.setColumnWidth(self.COL_PRICE_DONGJEOK, 80)
        self.tableWidget.setColumnWidth(self.COL_PRICE_JUNGJEOK, 80)
        self.tableWidget.setColumnWidth(self.COL_GERRERAYNG, 60)
        self.tableWidget.setColumnWidth(self.COL_BALDONG_TIME, 60)
        self.tableWidget.setColumnWidth(self.COL_HEJI_TIME, 60)
        self.tableWidget.setColumnWidth(self.COL_BALDONG_PRICE, 60)
        self.tableWidget.setColumnWidth(self.COL_HOGA, 90)
        self.tableWidget.setColumnWidth(self.COL_VI_COUNT, 30)
        self.tableWidget.setColumnWidth(self.COL_ORDERNUM, 60)
        self.tableWidget.setColumnWidth(self.COL_COUNT_BOUGHT, 50)
        self.tableWidget.setColumnWidth(self.COL_COUNT_NOTYET, 50)
        self.tableWidget.setColumnWidth(self.COL_BUY_PRICE, 60)
        self.tableWidget.setColumnWidth(self.COL_SELL_PRICE, 60)
        self.tableWidget.setColumnWidth(self.COL_CUR_PRICE, 60)
        self.tableWidget.setColumnWidth(self.COL_PROFIT_PRICE, 60)
        self.tableWidget.setColumnWidth(self.COL_PROFIT_PERCENT, 50)
        self.tableWidget.setColumnWidth(self.COL_STATUS, 60)
        self.tableWidget.setColumnWidth(self.COL_WON_TO_BUY, 60)
        self.tableWidget.setColumnWidth(self.COL_BTN_MESU, 40)
        self.tableWidget.setColumnWidth(self.COL_BTN_MEDO30, 40)
        self.tableWidget.setColumnWidth(self.COL_BTN_MEDO100, 40)
        self.tableWidget.setColumnWidth(self.COL_BTN_AUTO, 40)
        self.tableWidget.horizontalHeader().setSectionResizeMode(self.COL_CUR_PRICE, QHeaderView.Stretch)

        return self.tableWidget

    # def buyListGroup(self):
    #     buytabs = QTabWidget()
    #     buytabs.addTab(self.buytab1(), '주문 정보')
    #     buytabs.addTab(self.buytab2(), '주문 옵션')
    #     return buytabs
    #
    # def buytab1(self):
    #     self.tableWidget2 = QTableWidget(self)
    #     self.tableWidget2.setColumnCount(15)
    #     # self.tableWidget2.setMaximumHeight(150)
    #     self.tableWidget2.setEditTriggers(QAbstractItemView.NoEditTriggers)
    #     column_headers = ['요청시간', '체결시간', '주문번호', '코드', '종목', '수량', '미체결', '매수가', '매도가', '현재가', '평가손익', '수익률(%)', '매도호가', '상태', '매도or취소']
    #     self.tableWidget2.setHorizontalHeaderLabels(column_headers)
    #     self.tableWidget2.verticalHeader().setVisible(True)
    #     # self.tableWidget2.cellClicked.connect(self.newsTable2Clicked)
    #
    #     delegate = AlignDelegate(self.tableWidget2)
    #     self.tableWidget2.setItemDelegateForColumn(self.COL_CODE delegate)
    #     self.tableWidget2.setItemDelegateForColumn(1, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(2, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(3, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(4, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(5, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(6, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(7, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(8, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(9, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(10, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(11, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(12, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(13, delegate)
    #     self.tableWidget2.setItemDelegateForColumn(14, delegate)
    #
    #     self.tableWidget2.setColumnWidth(self.COL_CODE 80)
    #     self.tableWidget2.setColumnWidth(1, 80)
    #     self.tableWidget2.setColumnWidth(2, 80)
    #     self.tableWidget2.setColumnWidth(3, 70)
    #     self.tableWidget2.setColumnWidth(4, 100)
    #     self.tableWidget2.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
    #     self.tableWidget2.setColumnWidth(5, 50)
    #     self.tableWidget2.setColumnWidth(6, 50)
    #     self.tableWidget2.setColumnWidth(7, 80)
    #     self.tableWidget2.setColumnWidth(8, 80)
    #     self.tableWidget2.setColumnWidth(9, 180)
    #     self.tableWidget2.setColumnWidth(10, 80)
    #     self.tableWidget2.setColumnWidth(11, 80)
    #     self.tableWidget2.setColumnWidth(12, 80)
    #     self.tableWidget2.setColumnWidth(13, 80)
    #     self.tableWidget2.setColumnWidth(14, 80)
    #
    #     vbox = QVBoxLayout()
    #     vbox.addWidget(self.tableWidget2)
    #
    #     buytab1 = QWidget()
    #     buytab1.setLayout(vbox)
    #
    #     return buytab1

    def buytab2(self):
        widget = QWidget(self)
        grid = QGridLayout(widget)
        grid.addWidget(self.buytab2_1(), 0, 0, 0, 1)
        grid.addWidget(self.buytab2_2(), 0, 1, 0, 1)
        grid.addWidget(self.buytab2_3(), 0, 2, 0, 1)
        tab = QWidget()
        tab.setLayout(grid)
        return tab

    def buytab2_1(self):
        self.spinboxBuyPercentLabel = QLabel('VI해제 시초가 대비 x% 이상 오를 때 구매')
        self.spinboxBuyPercentLimit = QDoubleSpinBox()
        self.spinboxBuyPercentLimit.setMinimum(0.0)
        self.spinboxBuyPercentLimit.setMaximum(10)
        self.spinboxBuyPercentLimit.setSingleStep(0.1)
        self.spinboxBuyPercentLimit.valueChanged.connect(self.buyPercentChanged)
        self.spinboxBuyPercentLimit.setValue(self.BUY_START_PERCENT)

        self.spinboxLowLimitLabel = QLabel('손절 퍼센트(%) - 이하 시 전량 매도')
        self.spinboxLowLimit = QDoubleSpinBox()
        self.spinboxLowLimit.setMinimum(-10)
        self.spinboxLowLimit.setMaximum(0)
        self.spinboxLowLimit.setSingleStep(0.1)
        self.spinboxLowLimit.valueChanged.connect(self.lowLimitChanged)
        self.spinboxLowLimit.setValue(self.SELL_LOW_CUTLINE_PERCENT)

        self.spinboxHighLimitLabel = QLabel('익절 퍼센트(%) - 이상 시 30% 매도, x2 마다 30% 매도 반복, 10% 남으면 전량 매도')
        self.spinboxHighLimit = QDoubleSpinBox()
        self.spinboxHighLimit.setMinimum(0)
        self.spinboxHighLimit.setMaximum(100)
        self.spinboxHighLimit.setSingleStep(0.1)
        self.spinboxHighLimit.valueChanged.connect(self.highLimitChanged)
        self.spinboxHighLimit.setValue(self.SELL_HIGH_CUTLINE_PERCENT)

        self.spinboxSellTimeLabel = QLabel('강제매도시작시간(초) - 손절=익절 사이 에서 정체 시 시간 지나면 전량 매도')
        self.spinboxSellTime = QSpinBox()
        self.spinboxSellTime.setMinimum(0)
        self.spinboxSellTime.setMaximum(86400)
        self.spinboxSellTime.setSingleStep(10)
        self.spinboxSellTime.valueChanged.connect(self.sellTimeChanged)
        self.spinboxSellTime.setValue(self.SELL_CUTLINE_TIMESEC)

        vbox = QVBoxLayout()
        vbox.addWidget(self.spinboxBuyPercentLabel)
        vbox.addWidget(self.spinboxBuyPercentLimit)
        vbox.addWidget(self.spinboxLowLimitLabel)
        vbox.addWidget(self.spinboxLowLimit)
        vbox.addWidget(self.spinboxHighLimitLabel)
        vbox.addWidget(self.spinboxHighLimit)
        vbox.addWidget(self.spinboxSellTimeLabel)
        vbox.addWidget(self.spinboxSellTime)

        buytab2_1 = QWidget()
        buytab2_1.setLayout(vbox)
        return buytab2_1

    def buyPercentChanged(self):
        self.BUY_START_PERCENT = self.spinboxBuyPercentLimit.value()
        print(f'{common.getCurDateTime()}_[{self.NAME}][buyPercentChanged] {self.BUY_START_PERCENT} {type(self.BUY_START_PERCENT)}')
        self.saveOptionFile()

    def lowLimitChanged(self):
        self.SELL_LOW_CUTLINE_PERCENT = self.spinboxLowLimit.value()
        print(f'{common.getCurDateTime()}_[{self.NAME}][lowLimitChanged] {self.SELL_LOW_CUTLINE_PERCENT} {type(self.SELL_LOW_CUTLINE_PERCENT)}')
        self.saveOptionFile()

    def highLimitChanged(self):
        self.SELL_HIGH_CUTLINE_PERCENT = self.spinboxHighLimit.value()
        print(f'{common.getCurDateTime()}_[{self.NAME}][highLimitChanged] {self.SELL_HIGH_CUTLINE_PERCENT} {type(self.SELL_HIGH_CUTLINE_PERCENT)}')
        self.saveOptionFile()

    def sellTimeChanged(self):
        self.SELL_CUTLINE_TIMESEC = int(self.spinboxSellTime.value())
        print(f'{common.getCurDateTime()}_[{self.NAME}][sellTimeChanged] {self.SELL_CUTLINE_TIMESEC} {type(self.SELL_CUTLINE_TIMESEC)}')
        self.saveOptionFile()

    def minBuyGereryang(self):
        self.BUY_MIN_GERERYANG = int(self.spinboxMinGereryang.value())
        print(f'{common.getCurDateTime()}_[{self.NAME}][minBuyGereryangChanged] {self.BUY_MIN_GERERYANG}')
        self.saveOptionFile()

    def minBuyProfitPercent(self):
        self.BUY_PROFIT_PERCENT = int(self.spinboxProfitPercent.value())
        print(f'{common.getCurDateTime()}_[{self.NAME}][minBuyProfitChanged] {self.BUY_PROFIT_PERCENT} {type(self.BUY_PROFIT_PERCENT)}')
        self.saveOptionFile()

    def minBuyChanged(self):
        self.BUY_MINIMUM_COST_MANWON = int(self.spinboxMinBuyValue.value())
        # self.BUY_MINIMUM_COST_WON = self.BUY_MINIMUM_COST_MANWON * 10000
        # print(f'{common.getCurDateTime()}_[{self.NAME}][minBuyChanged] {self.BUY_MINIMUM_COST_WON} {type(self.BUY_MINIMUM_COST_WON)}')
        self.saveOptionFile()

    def secWaitChanged(self):
        self.SEC_WAIT_SELL_AFTER_BUY = int(self.spinboxSecWaitAfterBuy.value())
        print(f'{common.getCurDateTime()}_[{self.NAME}][secWaitChanged] {self.SEC_WAIT_SELL_AFTER_BUY} {type(self.SEC_WAIT_SELL_AFTER_BUY)}')
        self.saveOptionFile()

    def buytab2_2(self):
        self.spinboxMinGereryangLabel = QLabel('매수종목 최소 거래량')
        self.spinboxMinGereryang = QSpinBox()
        self.spinboxMinGereryang.setMinimum(0)
        self.spinboxMinGereryang.setMaximum(10000000)
        self.spinboxMinGereryang.setSingleStep(10000)
        self.spinboxMinGereryang.valueChanged.connect(self.minBuyGereryang)
        self.spinboxMinGereryang.setValue(self.BUY_MIN_GERERYANG)

        self.spinboxProfitPercentLabel = QLabel('전년동기대비(%) 이상')
        self.spinboxProfitPercent = QSpinBox()
        self.spinboxProfitPercent.setMinimum(1)
        self.spinboxProfitPercent.setMaximum(100000)
        self.spinboxProfitPercent.setSingleStep(1)
        self.spinboxProfitPercent.valueChanged.connect(self.minBuyProfitPercent)
        self.spinboxProfitPercent.setValue(self.BUY_PROFIT_PERCENT)

        self.spinboxMinBuyValueLabel = QLabel('매수금액(만원)')
        self.spinboxMinBuyValue = QSpinBox()
        self.spinboxMinBuyValue.setMinimum(10)
        self.spinboxMinBuyValue.setMaximum(10000)
        self.spinboxMinBuyValue.setSingleStep(10)
        self.spinboxMinBuyValue.valueChanged.connect(self.minBuyChanged)
        self.spinboxMinBuyValue.setValue(self.BUY_MINIMUM_COST_MANWON)

        self.spinboxSecWaitAfterBuyLabel = QLabel('최초매수 후 매도금지 대기시간(초)')
        self.spinboxSecWaitAfterBuy = QSpinBox()
        self.spinboxSecWaitAfterBuy.setMinimum(0)
        self.spinboxSecWaitAfterBuy.setMaximum(300)
        self.spinboxSecWaitAfterBuy.setSingleStep(1)
        self.spinboxSecWaitAfterBuy.valueChanged.connect(self.secWaitChanged)
        self.spinboxSecWaitAfterBuy.setValue(self.SEC_WAIT_SELL_AFTER_BUY)

        vbox = QVBoxLayout()
        vbox.addWidget(self.spinboxMinGereryangLabel)
        vbox.addWidget(self.spinboxMinGereryang)
        vbox.addWidget(self.spinboxProfitPercentLabel)
        vbox.addWidget(self.spinboxProfitPercent)
        vbox.addWidget(self.spinboxMinBuyValueLabel)
        vbox.addWidget(self.spinboxMinBuyValue)
        vbox.addWidget(self.spinboxSecWaitAfterBuyLabel)
        vbox.addWidget(self.spinboxSecWaitAfterBuy)

        buytab2_2 = QWidget()
        buytab2_2.setLayout(vbox)
        return buytab2_2

    def buytab2_3(self):
        self.mesuvi_all_radio = QRadioButton('상승/하락 VI 매수', self)
        self.mesuvi_all_radio.clicked.connect(self.mesuvi_all_radio_clicked)
        self.mesuvi_up_radio = QRadioButton('상승VI만 매수', self)
        self.mesuvi_up_radio.clicked.connect(self.mesuvi_up_radio_clicked)
        self.mesuvi_down_radio = QRadioButton('하락VI만 매수', self)
        self.mesuvi_down_radio.clicked.connect(self.mesuvi_down_radio_clicked)
        if self.mesuvi_type == 1:
            self.mesuvi_all_radio.setChecked(True)
        elif self.mesuvi_type == 2:
            self.mesuvi_up_radio.setChecked(True)
        elif self.mesuvi_type == 3:
            self.mesuvi_down_radio.setChecked(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.mesuvi_all_radio)
        vbox.addWidget(self.mesuvi_up_radio)
        vbox.addWidget(self.mesuvi_down_radio)

        buytab2_3 = QWidget()
        buytab2_3.setLayout(vbox)
        return buytab2_3

    def mesuvi_all_radio_clicked(self):
        self.mesuvi_type = 1
        print(f'{common.getCurDateTime()}_[{self.NAME}][mesuhoga1_radio_clicked] 매도호가: {self.mesuvi_type}')
        self.saveOptionFile()

    def mesuvi_up_radio_clicked(self):
        self.mesuvi_type = 2
        print(f'{common.getCurDateTime()}_[{self.NAME}][mesuvi_up_radio_clicked] 매도호가: {self.mesuvi_type}')
        self.saveOptionFile()

    def mesuvi_down_radio_clicked(self):
        self.mesuvi_type = 3
        print(f'{common.getCurDateTime()}_[{self.NAME}][mesuvi_down_radio_clicked] 매도호가: {self.mesuvi_type}')
        self.saveOptionFile()

    def tableWidgetSyncBtnClicked(self):
        self.tableWidget.clear()
        self.MYSTOCK.clear_all_stocks()
        for row in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(row)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        column_headers = ['코드', '종목명', '시가대비\n등락률', '기준가격\n동적VI', '기준가격\n정적VI', '거래량', '발동', '해지', '발동가격', '호가',
                          '횟수', '주문번호', '수량', '미체결', '매수가', '매도가', '현재가', '평가손익', '수익률', '상태', '금액(만)', '매수', '매도', '매도', '오토']
        self.tableWidget.setHorizontalHeaderLabels(column_headers)
        self.tableWidget.verticalHeader().setVisible(True)
        self.KIWOOM.get_account_evaluation_balance()

    def tableWidgetPasswordBtnClicked(self):
        self.KIWOOM.showAccountWindow()

    def soundBtnClicked(self):
        if self.playSound:
            self.playSound = False
        else:
            self.playSound = True
        self.soundBtn.setText({False: "소리 꺼짐", True: "소리 켜짐"}[self.playSound])
        self.soundBtn.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % ({True: (0, 100, 250, 255, 255, 255), False: (50, 50, 0, 255, 255, 255)}[self.playSound]))
        print(f'{common.getCurDateTime()}_[{self.NAME}][soundBtn_clicked] playsound: {self.playSound}')

    @QtCore.pyqtSlot()
    def autoClicked(self):
        button = QtWidgets.qApp.focusWidget() #self.sender()
        item = self.tableWidget.indexAt(button.pos())
        code = self.tableWidget.item(item.row(), self.COL_CODE).text()
        status = self.tableWidget.item(item.row(), self.COL_STATUS).text()
        print(f'{common.getCurDateTime()}_[{self.NAME}][autoClicked] index at: {item.row()}, code: {code}, status: {status}')
        for stock in self.MYSTOCK.my_stocks:
            if stock.stock_code == code:
                # tempitem = self.tableWidget.cellWidget(item.row(), 22)
                print(f'{common.getCurDateTime()}_[{self.NAME}][autoClicked] stock.ALLOW_AUTO_BUYSELL: {stock.ALLOW_AUTO_BUYSELL}')
                if stock.ALLOW_AUTO_BUYSELL is True:
                    stock.ALLOW_AUTO_BUYSELL = False
                    button.setText('중지')
                    button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 0, 0, 255, 255, 255))
                else:
                    stock.ALLOW_AUTO_BUYSELL = True
                    button.setText('오토')
                    button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 200, 0, 255, 255, 255))
                # self.tableWidget.setCellWidget(item.row(), 22, tempitem)

    def spintoBuyClicked(self):
        value = self.spinboxToBuy.value()
        button = QtWidgets.qApp.focusWidget()
        item = self.tableWidget.indexAt(button.pos())
        print(f'{common.getCurDateTime()}_[{self.NAME}][spintoBuyClicked] button.pos(): {button.pos()}, value: {value} {type(value)}')
        code = self.tableWidget.item(item.row(), self.COL_CODE).text()
        for stock in self.MYSTOCK.my_stocks:
            if stock.stock_code == code:
                stock.n_won_to_buy = value
                print(f'{common.getCurDateTime()}_[{self.NAME}][spintoBuyClicked] code: {code}, n_won_to_buy changed to: {value} {type(value)}')

    def buyClicked(self):
        button = QtWidgets.qApp.focusWidget()
        item = self.tableWidget.indexAt(button.pos())
        code = self.tableWidget.item(item.row(), self.COL_CODE).text()
        cur_quantity = int(self.tableWidget.item(item.row(), self.COL_COUNT_BOUGHT).text())
        status = self.tableWidget.item(item.row(), self.COL_STATUS).text()
        hoga = common.convertStringMoneyToInt(self.tableWidget.item(item.row(), self.COL_HOGA).text().split('(')[0])
        minimum_manwon = int(self.tableWidget.cellWidget(item.row(), self.COL_WON_TO_BUY).value())
        minimum_won = minimum_manwon * 10000
        print(f'{common.getCurDateTime()}_[{self.NAME}][buyClicked] minimum_manwon: {minimum_manwon}, minimum_won: {minimum_won}')
        try:
            to_buy = trunc(int(minimum_won / hoga)) - 1
        except:
            to_buy = 0
        try:
            notyet_quantity = int(self.tableWidget.item(item.row(), self.COL_COUNT_NOTYET).text())
            order_no = self.tableWidget.item(item.row(), self.COL_ORDERNUM).text()
        except:
            notyet_quantity = 0
        print(f'{common.getCurDateTime()}_[{self.NAME}][buyClicked] index at: {item.row()}, code: {code}, cur_quantity: {cur_quantity}, notyet_quantity: {notyet_quantity}, status:{status}')
        if notyet_quantity > 0:
            # 취소가능
            self.tableWidget.setItem(item.row(), self.COL_BTN_MEDO30, QTableWidgetItem('취소'))
            print(f'{common.getCurDateTime()}_[{self.NAME}][buyClicked] cancel all', code, 'quantity', cur_quantity)
            if code != '-':
                self.KIWOOM.stock_cancel_all(code, cur_quantity, self.buy_sell_screen_no, order_no)
                button.setText('매수')
                button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (250, 50, 0, 255, 255, 255))
        else:
            print(f'{common.getCurDateTime()}_[{self.NAME}][buyClicked] buy:', code, 'quantity', cur_quantity)
            if code != '-':
                self.KIWOOM.stock_buy_more(code, to_buy, self.buy_sell_screen_no)
                for stock in self.MYSTOCK.my_stocks:
                    if stock.stock_code == code:
                        stock.firstbuytime = time.time()
                        stock.n_BUY_DONE = True
                button.setText('취소')
                button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (200, 200, 0, 255, 255, 255))
                self.KIWOOM.addRealTimeRegCode(code)
                self.KIWOOM.startRealtimeMonitor()

    def sell30Clicked(self):
        # button = self.sender()
        button = QtWidgets.qApp.focusWidget()
        item = self.tableWidget.indexAt(button.pos())
        code = self.tableWidget.item(item.row(), self.COL_CODE).text()
        cur_quantity = int(self.tableWidget.item(item.row(), self.COL_COUNT_BOUGHT).text())
        status = self.tableWidget.item(item.row(), self.COL_STATUS).text()
        try:
            notyet_quantity = int(self.tableWidget.item(item.row(), self.COL_COUNT_NOTYET).text())
            order_no = self.tableWidget.item(item.row(), self.COL_ORDERNUM).text()
        except:
            notyet_quantity = 0
        print(f'{common.getCurDateTime()}_[{self.NAME}][sell30Clicked] index at: {item.row()}, code: {code}, cur_quantity: {cur_quantity}, notyet_quantity: {notyet_quantity}, status:{status}')
        if notyet_quantity > 0:
            # 취소가능
            self.tableWidget.setItem(item.row(), self.COL_BTN_MEDO30, QTableWidgetItem('취소'))
            print(f'{common.getCurDateTime()}_[{self.NAME}][sellAllClicked] cancel all', code, 'quantity', cur_quantity)
            if code != '-':
                self.KIWOOM.stock_cancel_all(code, cur_quantity, self.buy_sell_screen_no, order_no)
                button.setText('30%')
                button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 50, 200, 255, 255, 255))
        else:
            print(f'{common.getCurDateTime()}_[{self.NAME}][sellAllClicked] sell all', code, 'quantity', cur_quantity)
            if code != '-':
                to_sell = trunc(cur_quantity * 0.3) - 1
                self.KIWOOM.stock_sell_single_manual(code, to_sell)
                button.setText('취소')
                button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (200, 200, 0, 255, 255, 255))

    def sellAllClicked(self):
        # button = self.sender()
        button = QtWidgets.qApp.focusWidget()
        item = self.tableWidget.indexAt(button.pos())

        # self.buy_sell_screen_no += 1
        # if self.buy_sell_screen_no > 7100:
        #     self.buy_sell_screen_no = 7000
        # x = self.tableWidget.selectedIndexes()
        code = self.tableWidget.item(item.row(), self.COL_CODE).text()
        cur_quantity = int(self.tableWidget.item(item.row(), self.COL_COUNT_BOUGHT).text())
        status = self.tableWidget.item(item.row(), self.COL_STATUS).text()
        try:
            notyet_quantity = int(self.tableWidget.item(item.row(), self.COL_COUNT_NOTYET).text())
            order_no = self.tableWidget.item(item.row(), self.COL_ORDERNUM).text()
        except:
            notyet_quantity = 0

        print(f'{common.getCurDateTime()}_[{self.NAME}][sellAllClicked] index at: {item.row()}, code: {code}, cur_quantity: {cur_quantity}, notyet_quantity: {notyet_quantity}, status:{status}')

        if notyet_quantity > 0:
            # 취소가능
            self.tableWidget.setItem(item.row(), self.COL_BTN_MEDO30, QTableWidgetItem('취소'))
            print(f'{common.getCurDateTime()}_[{self.NAME}][sellAllClicked] cancel all', code, 'quantity', cur_quantity)
            if code != '-':
                self.KIWOOM.stock_cancel_all(code, cur_quantity, self.buy_sell_screen_no, order_no)
                button.setText('100%')
                button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (0, 50, 250, 255, 255, 255))
        else:
            print(f'{common.getCurDateTime()}_[{self.NAME}][sellAllClicked] sell all', code, 'quantity', cur_quantity)
            if code != '-':
                self.KIWOOM.stock_sell_all_manual(code, cur_quantity, self.buy_sell_screen_no)
                button.setText('취소')
                button.setStyleSheet('background-color:rgb(%s,%s,%s);color:rgb(%s,%s,%s)' % (200, 200, 0, 255, 255, 255))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)

    GLOBAL_DATA_QUEUE = Queue()
    GLOBAL_ORDER_QUEUE = Queue()

    mainWindow = MainWindow()
    mainWindow.show()

    app.exec_()