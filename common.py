import datetime
import time
import ctypes

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QPushButton

def error_popup(title, msg):
    ctypes.windll.user32.MessageBoxW(0, msg, title, 0)

def info_popup(self, title, msg):
    self.dialog = QDialog()
    button = QPushButton(msg)
    button.clicked.connect(popupOpen(self.dialog, title, msg))
    button.setGeometry(10, 10, 200, 50)

def popupOpen(dialog, title, msg):
    dialog.setWindowTitle(title)
    dialog.setWindowModality(Qt.ApplicationModal)
    dialog.resize(300, 200)
    dialog.show()

def getCurDateTime():
    # return time.strftime("%Y%m%d_%H%M%S")
    return datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S.%f')[:-2]

def getCurDate():
    return time.strftime("%Y%m%d")

def getCurPcTime():
    curtime = time.localtime()
    if (curtime.tm_hour < 10):
        hour = '0' + str(curtime.tm_hour)
    else:
        hour = str(curtime.tm_hour)
    if (curtime.tm_min < 10):
        min = '0' + str(curtime.tm_min)
    else:
        min = str(curtime.tm_min)
    if curtime.tm_sec < 10:
        sec = '0' + str(curtime.tm_sec)
    else:
        sec = str(curtime.tm_sec)
    pctime = hour + ':' + min + ':' + sec
    return pctime

def findByWords(sentence, news_matching):
    print('[findByWords] news_matching size: ' + str(len(news_matching)))
    for word in news_matching:
        print('[findByWords] finding word: ' + word)
        val = word in sentence
        if val:
            print('[findByWords] ' + sentence + ': ' + word + ' Found! True')
            return True
    print('[findByWords] ' + sentence + ', False')
    return False


def findByWordsCustom(sentence, news_matching_custom):
    return_list = []
    print('[findByWordsCustom] news_matching_custom size: ' + str(len(news_matching_custom)))
    for word in news_matching_custom:
        print('[findByWordsCustom] finding word: ' + word)
        val = word in sentence
        if val:
            codes_str = news_matching_custom[word]
            print('[findByWordsCustom] ' + sentence + ': ' + word + ' Found! True - ' + codes_str)
            return_list = codes_str.split(';')
            return return_list
    print('[findByWordsCustom] ' + sentence + ', False')
    return return_list

def convertStringMoneyToInt(number):
    try:
        if number == '' or number is None:
            return 0
        else:
            return int(number.replace('+', '').replace('-', '').replace(',', ''))
    except:
        return 0

def convertNumberToWon(number):
    strnum = str(number)
    temp_num = ''
    if len(strnum) < 10:
        temp_num = strnum[:-6] + ',' + strnum[-6:-3] + ',' + strnum[-3:] + '원'
    else:
        temp_num = '1,000,000,000원'
    return temp_num

def convertNumberToMoney(number):
    try:
        val = int(number)
        return format(val, ',')
    except ValueError:
        if len(number) == 0:
            return 0
        if number[0] == '+' or number[0] == '-':
            val = int(number.replace(',', ''))
            return format(val, ',')
        else:
            return number

def shrinkNewsTitle(title):
    new_title = title.replace("・", "").replace(u"\u318D", "").replace(u"\u00B7", "").replace(u"\u30FB", "").replace("\xa0", "").replace("&nbsp;", "").replace("& ;", "").replace("…", "").replace("・", "").replace("・・・", "").replace("·", "").replace("···", "").replace(".", "").replace(" ", "").replace("˝", "").replace(".", "").replace('”', "").replace("'", "").replace('"', "").replace('`', "").replace(',', "").replace('“', "").replace('‘', "").replace('’', "").replace('·', "").replace(':', "").replace('(', "").replace(')', "").replace('[', "").replace(']', "").replace('<', "").replace('>', "").replace('&nbsp;', "").replace('&amp;', "").replace('amp;', "").replace('&lt;', "").replace('&#39', "").replace('&gt;', "").replace('&', "").strip()
    try:
        cut_back = new_title[:10]
    except Exception as e:
        cut_back = new_title
        print(f'{getCurDateTime()}_[shrinkNewsTitle] Title: {new_title}, Exception: {e}')
    # print(f'[shrinkNewsTitle] cut_back_pos: {cut_back_pos}, cut_back: {cut_back}, ori: {new_title}')
    return cut_back

def removeSharpIfHasOne(word):
    # 매칭에 #이 있는지 확인, #있는넘만 매수
    if len(word) > 0 and word[0] == '#':
        return word.replace('#', '').replace('@', '')
    else:
        return word

def checkMatchingToBuy(word, self_name, n_name):
    # 매칭에 #이 있는지 확인, #있는넘만 매수
    if len(word) > 0 and word[0] == '#' or len(word) > 1 and word[1] == '#':
        print(f'{getCurDateTime()}_[{self_name}][{n_name}] word: {word}, has #, 매수 진행 필요')
        return True
    else:
        # print(f'{getCurDateTime()}_[{self_name}][{n_name}] word: {word}, has no #')
        return False

def findStockFromTitle(kospi_dic_by_name_main, title, n_name):
    # title = '아모레과 삼성전자와 LG전자가 다 같이 ...ㅋㅋㅋㅋ' = 아모레퍼시픽이 택 되어야함
    # 삼성전자 , 아모레, LG전자가 골라지고 가장 앞 포지션 아모레가 채택
    # 에스엘 - 에스엘바이오닉스이 코리아를 제치고 상한가를 친다 = 에스엘이 아닌 에스엘바이오닉스가 택 되어야함
    # 에스엘, 에스엘바이오닉스, 코리아가 골라지고
    # 레이 - 슈퍼레이저쎌이 상한가를 친다 = 레이가 아닌 레이저쎌이 택 되어야함
    # 레이, 슈퍼레이저쏄
    name = '-'
    wordpos = -1
    result_list = []
    for key in kospi_dic_by_name_main:
        # print('[findStockFromTitle] checking ', key, 'in', title)
        if key != '' and key != ' ' and key in title:
            result_list.append(key)
            newpos = title.find(key)
            if wordpos == -1:
                wordpos = newpos
                name = key
                # print(f'[findStockFromTitle] Found one, {name}, pos, {str(newpos)}')
            else:
                if wordpos > newpos:
                    wordpos = newpos
                    name = key
                    # print(f'[findStockFromTitle] Front pos, change to {name}, pos, {str(newpos)}')
                # else:
                    # print(f'[findStockFromTitle] {name}, pos, {str(newpos)} its behind, pass')
    finalname = name
    # print(f'[{n_name}][findStockFromTitle] stock name is', finalname, 'stock list is', result_list)
    for listname in result_list:
        if finalname in listname:
            if len(finalname) < len(listname):
                finalname = listname
                # print(f'[{n_name}][findStockFromTitle] final stock name is replaced from', name, 'to', finalname)
    return finalname

def error_code_list(code):
    """ 키움개발가이드 오류코드 목록 """
    error_code = {0: ('OP_ERR_NONE', '정상처리'),
                  -10: ('OP_ERR_FAIL', '실패'),
                  -100: ('OP_ERR_LOGIN', '사용자정보교환실패'),
                  -101: ('OP_ERR_CONNECT', '서버접속실패'),
                  -102: ('OP_ERR_VERSION', '버전처리실패'),
                  -103: ('OP_ERR_FIREWALL', '개인방화벽실패'),
                  -104: ('OP_ERR_MEMORY', '메모리보호실패'),
                  -105: ('OP_ERR_INPUT', '함수입력값오류'),
                  -106: ('OP_ERR_SOCKET_CLOSED', '통신연결종료'),
                  -200: ('OP_ERR_SISE_OVERFLOW', '시세조회과부하'),
                  -200: ('OP_ERR_SISE_OVERFLOW', '시세조회과부하'),
                  -201: ('OP_ERR_RQ_STRUCT_FAIL', '전문작성초기화실패'),
                  -202: ('OP_ERR_RQ_STRING_FAIL', '전문작성입력값오류'),
                  -203: ('OP_ERR_NO_DATA', '데이터없음.'),
                  -204: ('OP_ERR_OVER_MAX_DATA', '조회가능한종목수초과'),
                  -205: ('OP_ERR_DATA_RCV_FAIL', '데이터수신실패'),
                  -206: ('OP_ERR_OVER_MAX_FID', '조회가능한FID수초과'),
                  -207: ('OP_ERR_REAL_CANCEL', '실시간해제오류'),
                  -300: ('OP_ERR_ORD_WRONG_INPUT', '입력값오류'),
                  -301: ('OP_ERR_ORD_WRONG_ACCTNO', '계좌비밀번호없음'),
                  -302: ('OP_ERR_OTHER_ACC_USE', '타인계좌사용오류'),
                  -303: ('OP_ERR_MIS_2BILL_EXC', '주문가격이20억원을초과'),
                  -304: ('OP_ERR_MIS_5BILL_EXC', '주문가격이50억원을초과'),
                  -305: ('OP_ERR_MIS_1PER_EXC', '주문수량이총발행주수의1%초과오류'),
                  -306: ('OP_ERR_MIS_3PER_EXC', '주문수량은총발행주수의3%초과오류'),
                  -307: ('OP_ERR_SEND_FAIL', '주문전송실패'),
                  -308: ('OP_ERR_ORD_OVERFLOW', '주문전송과부하'),
                  -309: ('OP_ERR_MIS_300CNT_EXC', '주문수량300계약초과'),
                  -310: ('OP_ERR_MIS_500CNT_EXC', '주문수량500계약초과'),
                  -340: ('OP_ERR_ORD_WRONG_ACCTINFO', '계좌정보없음'),
                  -500: ('OP_ERR_ORD_SYMCODE_EMPTY', '종목코드없음')}
    ret = error_code[code][1]
    return ret