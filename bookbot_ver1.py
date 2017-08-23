#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import books

reload(sys)
sys.setdefaultencoding('utf-8')

from concurrent import futures
import time
import argparse
import grpc
from google.protobuf import empty_pb2
import pymysql
import os
import smtplib          #메일발송을 위한 모듈
from email.mime.text import MIMEText
import xml.etree.ElementTree as ET
import urllib2
import urllib



exe_path = os.path.realpath(sys.argv[0])
bin_path = os.path.dirname(exe_path)
lib_path = os.path.realpath(bin_path + '/../lib/python')
sys.path.append(lib_path)

from proto import pool_pb2
from proto import sds_pb2
from proto import provider_pb2
from proto import userattr_pb2

# import MySQLdb.cursors

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def sendMail(text):                                      #메일발송
    HOST = 'smtp.gmail.com'
    me = 'aitutor123@gmail.com'
    you = 'songcchiyoon@gmail.com'   #me가 내용을 보낼 메일 주소.
    contents = text                   #text로
    msg = MIMEText(contents, _charset='euc-kr')
    msg['Subject'] = '[ALERT]'
    msg['From'] = me
    msg['To'] = you

    s = smtplib.SMTP(HOST, 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("aitutor123@gmail.com", "xbxj1234")   #접근을 위해 보안등급이 낮은 메일로 구축.
    s.sendmail(me, [you], msg.as_string())
    s.quit()

class ordercof_simple_DA(provider_pb2.DialogAgentProviderServicer):
    # STATE
    # state = provider_pb2.DIAG_STATE_IDLE
    init_param = provider_pb2.InitParameter()

    # PROVIDER
    provider = pool_pb2.DialogAgentProviderParam()
    provider.name = 'search_1'                              #sds프로젝트 이름
    provider.description = 'simply order for tutor'
    provider.version = '0.1'
    provider.single_turn = False
    provider.agent_kind = pool_pb2.AGENT_SDS
    provider.require_user_privacy = True

    # SDS Stub
    sds_server_addr = ''
    sds_stub = None

    def __init__(self):
        self.state = provider_pb2.DIAG_STATE_IDLE

    #
    # INIT or TERM METHODS
    #
    def convertXMLtoObjects(self, root):
        book_list = []
        for channel in root:
            for item in channel.findall('item'):
                book = books.books()
                if item.find('title') is not None:
                    title = item.find('title').text.encode("utf-8")
                    book.setTitle(title)
                if item.find('author') is not None:
                    author = item.find('author').text.encode("utf-8")
                    book.setAuthoor(author)
                if item.find('link') is not None:
                    link = item.find('link').text.encode("utf-8")
                    book.setLink(link)
                if item.find('image') is not None:
                    image = item.find('image').text.encode("utf-8")
                    book.setImageURL(image)
                if item.find('price') is not None:
                    price = item.find('price').text.encode("utf-8")
                    book.setPrice(price)
                if item.find('publisher') is not None:
                    pub = item.find('publisher').text.encode("utf-8")
                    book.setPublisher(pub)
                if item.find('description') is not None:
                    desc = item.find('description').text.encode("utf-8")
                    book.setDescription(desc)

                book_list.append(book)

        return book_list

    def query(self, id, pw, params, start_point):
        print "start query"
        encText = urllib.pathname2url(params)
        #title = urllib.pathname2url("윤태호")
        url = "https://openapi.naver.com/v1/search/book.xml?query=" + encText + "&display=10&start=1&sort=count"  # json 결과
        # url = "https://openapi.naver.com/v1/search/book_adv.xml?d_auth="+title+"&display=10&start=1"  # json 결과

        # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # xml 결과
        request = urllib2.Request(url)

        request.add_header("X-Naver-Client-Id", id)
        request.add_header("X-Naver-Client-Secret", pw)
        response = urllib2.urlopen(request)
        rescode = response.getcode()

        if (rescode == 200):
            response_body = response.read()
            result = response_body.decode("utf-8").encode('utf-8')
            # print(result)
            # print(result)
            tree = ET.ElementTree(ET.fromstring(result))

            root = tree.getroot()
            book_ruslts = self.convertXMLtoObjects(root)
            return book_ruslts

        else:
            print("Error Code:" + rescode)

    def query_detail(self,id, pw, params, theme):

        param = urllib.pathname2url(params)
        url = ""
        if theme == "title":
            url = "https://openapi.naver.com/v1/search/book_adv.xml?d_titl=" + param + "&display=5&start=1"  # json 결과
        elif theme == "author":
            url = "https://openapi.naver.com/v1/search/book_adv.xml?d_auth=" + param + "&display=5&start=1&sort=count"  # json 결과
        else:
            print("no")
        request = urllib2.Request(url)

        request.add_header("X-Naver-Client-Id", id)
        request.add_header("X-Naver-Client-Secret", pw)
        response = urllib2.urlopen(request)
        rescode = response.getcode()

        if (rescode == 200):
            response_body = response.read()
            result = response_body.decode("utf-8").encode('utf-8')
            # print(result)
            # print(result)
            tree = ET.ElementTree(ET.fromstring(result))

            root = tree.getroot()
            book_ruslts = self.convertXMLtoObjects(root)
            return book_ruslts

        else:
            print("Error Code:" + rescode)

    def get_sds_server(self):
        sds_channel = grpc.insecure_channel(self.init_param.sds_remote_addr)
        # sds_channel = grpc.insecure_channel('127.0.0.1:9906')
        resolver_stub = sds_pb2.SpokenDialogServiceResolverStub(sds_channel)

        print 'stub'
        sq = sds_pb2.ServiceQuery()
        sq.path = self.sds_path
        sq.name = self.sds_domain
        print sq.path, sq.name

        svc_loc = resolver_stub.Find(sq)
        print 'find result', svc_loc
        # Create SpokenDialogService Stub
        print 'find result loc: ', svc_loc.server_address
        self.sds_stub = sds_pb2.SpokenDialogServiceStub(
            grpc.insecure_channel(svc_loc.server_address))
        self.sds_server_addr = svc_loc.server_address
        print 'stub sds ', svc_loc.server_address

    def IsReady(self, empty, context):
        print 'IsReady', 'called'
        status = provider_pb2.DialogAgentStatus()
        status.state = self.state
        return status

    def Init(self, init_param, context):
        print 'Init', 'called'
        self.state = provider_pb2.DIAG_STATE_INITIALIZING
        # COPY ALL
        self.init_param.CopyFrom(init_param)
        # DIRECT METHOD
        self.sds_path = init_param.params['sds_path']
        print 'path'
        self.sds_domain = init_param.params['sds_domain']
        print 'domain'

        self.db_host = init_param.params['db_host']
        print 'db_host'

        self.db_port = init_param.params["db_port"]
        print 'db_port'

        self.db_user = init_param.params['db_user']
        print 'db_user'

        self.db_pwd = init_param.params['db_pwd']
        print 'db_pwd'

        self.db_database = init_param.params['db_database']
        print 'db_database'

        self.db_table = init_param.params['db_table']
        print 'db_table'

        # CONNECT
        self.get_sds_server()
        print 'sds called'
        self.state = provider_pb2.DIAG_STATE_RUNNING
        # returns provider
        result = pool_pb2.DialogAgentProviderParam()
        result.CopyFrom(self.provider)
        print 'result called'
        return result

    def Terminate(self, empty, context):
        print 'Terminate', 'called'
        # DO NOTHING
        self.state = provider_pb2.DIAG_STATE_TERMINATED
        return empty_pb2.Empty()

    #
    # PROPERTY METHODS
    #

    def GetProviderParameter(self, empty, context):
        print 'GetProviderParameter', 'called'
        result = pool_pb2.DialogAgentProviderParam()
        result.CopyFrom(self.provider)
        return result

    def GetRuntimeParameters(self, empty, context):
        print 'GetRuntimeParameters', 'called'
        params = []
        result = provider_pb2.RuntimeParameterList()

        sds_path = provider_pb2.RuntimeParameter()
        sds_path.name = 'sds_path'
        sds_path.type = userattr_pb2.DATA_TYPE_STRING
        sds_path.desc = 'DM Path'
        sds_path.default_value = 'search_1'        #sds명
        sds_path.required = True
        params.append(sds_path)

        sds_domain = provider_pb2.RuntimeParameter()
        sds_domain.name = 'sds_domain'
        sds_domain.type = userattr_pb2.DATA_TYPE_STRING
        sds_domain.desc = 'DM Domain'
        sds_domain.default_value = 'search_1'        #sds명
        sds_domain.required = True
        params.append(sds_domain)

        db_host = provider_pb2.RuntimeParameter()
        db_host.name = 'db_host'
        db_host.type = userattr_pb2.DATA_TYPE_STRING
        db_host.desc = 'Database Host'
        db_host.default_value = 'ai-tutor.cxofzcpmqwoz.us-west-2.rds.amazonaws.com'
        db_host.required = True
        params.append(db_host)

        db_port = provider_pb2.RuntimeParameter()
        db_port.name = 'db_port'
        db_port.type = userattr_pb2.DATA_TYPE_STRING
        db_port.desc = 'Database Port'
        db_port.default_value = '3306'
        db_port.required = True
        params.append(db_port)

        db_user = provider_pb2.RuntimeParameter()
        db_user.name = 'db_user'
        db_user.type = userattr_pb2.DATA_TYPE_STRING
        db_user.desc = 'Database User'
        db_user.default_value = 'aitutor'      #해당 database접속을 위한 user명
        db_user.required = True
        params.append(db_user)

        db_pwd = provider_pb2.RuntimeParameter()
        db_pwd.name = 'db_pwd'
        db_pwd.type = userattr_pb2.DATA_TYPE_STRING
        db_pwd.desc = 'Database Password'
        db_pwd.default_value = 'aitutor12'   #그리고 비밀번호
        db_pwd.required = True
        params.append(db_pwd)

        db_database = provider_pb2.RuntimeParameter()
        db_database.name = 'db_database'
        db_database.type = userattr_pb2.DATA_TYPE_STRING
        db_database.desc = 'Database Database name'
        db_database.default_value = 'tutor_3rd'       #database의 이름
        db_database.required = True
        params.append(db_database)

        db_table = provider_pb2.RuntimeParameter()     #DB만들면 여기 수정해야함. 테이블이름
        db_table.name = 'db_table'
        db_table.type = userattr_pb2.DATA_TYPE_STRING
        db_table.desc = 'Database table'
        db_table.default_value = 'mindscafe'                  #테이블명 입력!
        db_table.required = True
        params.append(db_table)


        result.params.extend(params)
        return result

    def Talk(self, talk, context):
        meta_data = {"out.embed.type": "", "out.embed.data.body": ""}       # meta data 초기화 => 여기서 meta data란 text형식으로 보여주는 것 이외에 비디오, 이미지, 음악재생 등의 추가 정보를 제공해 줄 수 있는 데이터
        flag = False

        self.get_sds_server()
        print '------- [talk 시작] --------'

        # talk에는 입력에 대한 정보가 들어있다.
        # ex) 접속 경로, 입력, 세션 등등..
        print 'talk ==> ', talk

        session_id = talk.session_id
        print "Session ID : " + str(session_id)  # 해당 session id
        print "[Question] ", talk.text  # talk.text -> 질문 내용
        print "Access_from", str(talk.access_from)  # 접속 경로( 안드로이드, ios, 스피커, 웹, console 등에 따라 다른 값으로 저장)

        # Create DialogSessionKey & set session_key
        dsk = sds_pb2.DialogueSessionKey()
        dsk.session_key = session_id
        print '<create session key for dialog>'

        # Dialog Open
        sds_session = self.sds_stub.Open(dsk)          # sds에서 설정해준 시나리오 open
        print '<Open the dialog>'

        sq = sds_pb2.SdsQuery()
        sq.session_key = sds_session.session_key

         # 실제로 sds에 입력을 넣는 부분.
        sq.utter = talk.text

        # Dialog UnderStand
        sds_act = self.sds_stub.Understand(sq)  # => 대화에 대한 전반적인 log. ex) 사용하는 slot

        # DB Connection
        conn = pymysql.connect(user=self.db_user,
                               password=self.db_pwd,
                               host=self.db_host,
                               database=self.db_database,
                               charset='utf8',
                               use_unicode=False)
        curs = conn.cursor()

        # 변수 설정
        meta_code = ''  # 메타데이터의 경로 값을 넣기 위한 변수
        #슬롯 변수 설정
        or_add = None
        or_useradd = None
        or_drink = None
        or_sand = None
        or_name=None
        or_phone=None

        pre_title = "pre"
        pre_search = "pre"
        or_title=None
        or_search=None
        or_query=None
        start_point = 1
        dialog_act = ''  # 대화의도를 받아 오기 위한 변수
        key = 'AIzaSyBsA8e5xHixD3RNYGMyITPiYlMsqdlIuyg'    #지도 html을 위한 key값
        client_id = "pQ9flPrSlR3iB2m7N0w4"
        client_secret = "M3Ziiv0li1"

        slot_list = []
        output = ''


        # Create SdsSlots & set Session Key
        sds_slots = sds_pb2.SdsSlots()
        sds_slots.session_key = sds_session.session_key
        print sds_act.filled_slots
        print '< sds_act > ', sds_act

        # Copy filled_slot to result Slot & Fill information slots
        for k, v in sds_act.filled_slots.items():
            sds_slots.slots[k] = v
        print 'sds_slots.slots', sds_slots.slots

        # Dialog Act                                      # DA TYPE을 이용하기 위한 파싱
        best_slu = sds_act.origin_best_slu
        print 'best_slu : ' + best_slu
        dialog_act = best_slu[best_slu.find('#') + 1:best_slu.find('(')]
        print 'dialog_act : ' + dialog_act

        if len(sds_act.filled_slots.keys()) > 0:                     # Talk함수가 실행 된 상황에서 SDS 채워진 슬롯값들을 sds_slots.slots에 메타 형식 (Dict)으로 삽입
            for i in range(0, len(sds_act.filled_slots.keys())):
                slot_list += [sds_act.filled_slots.keys()[i]]
        print 'slot_list : ', slot_list

        err = 'Dialog Agent 오류 메시지 입니다.'
        #확인할 슬롯을 구성하고, 그에 따른 변수 완성
        try:
            if sds_act.filled_slots.get('user.search') is not None:
                if pre_search != sds_act.filled_slots.get('user.search'):
                    or_search = sds_act.filled_slots.get('user.search')
                    pre_search = or_search
                print sds_act.filled_slots.get('user.search')

            if sds_act.filled_slots.get('user.title') is not None:
                if pre_title != sds_act.filled_slots.get('user.title'):
                    or_title = sds_act.filled_slots.get('user.title')
                    pre_title = or_title
                print sds_act.filled_slots.get('user.title')
            else:
                print "no title"
            '''if sds_act.filled_slots.get('user.address') is not None:
                or_useradd = sds_act.filled_slots.get('user.address')
                print sds_act.filled_slots.get('user.address')

            if sds_act.filled_slots.get('user.drink') is not None:
                or_drink = sds_act.filled_slots.get('user.drink')
                print sds_act.filled_slots.get('user.drink')
                
            if sds_act.filled_slots.get('user.sandwich') is not None:
                or_sand = sds_act.filled_slots.get('user.sandwich')
                print sds_act.filled_slots.get('user.sandwich')

            if sds_act.filled_slots.get('name') is not None:
                or_name = sds_act.filled_slots.get('name')
                print sds_act.filled_slots.get('name')

            if sds_act.filled_slots.get('phone') is not None:
                or_phone = sds_act.filled_slots.get('phone')
                print sds_act.filled_slots.get('phone')'''

            print '[sds_act.filled_slots](address, user.address, user.drink, user.sandwich, name, phone)', or_query

        except:
            flag = True
            print err
                             #대화의도에 따른 html을 삽입한다.
                             #슬롯 output에 따른 변수를 설정하고 해당 내용을 입력
        '''if dialog_act == 'search' and or_query is not None:
            if or_query is not None:
                #output = '잠시만 기다리시면 주문하신 메뉴를 신속히 배달해 드리겠습니다. 기다리시는 동안 재밌는 영상![END]'
                #sds_slots.slots['output'] = output
                print(type(or_query))
                param = or_query.encode("utf-8")
                books = self.query(client_id, client_secret, param)
                output = param +"에 대한 검색결과입니다."
                result = "<ul>"
                meta_code = ""
                for book in books:
                    result += "<li><b>"+book.Title() +"</b>/<b>"+book.Author()+"</b></li></p>"
                result += "</ul>"
                print "img :"+books[0].ImageURL()
                #result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
                #result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
                print "result : " + result
                meta_code += '<!DOCTYPE html> <html> <head> </head> <body>'+result+'</body> </html>'
                sdsUtter = self.sds_stub.FillSlots(sds_slots)
                sdsUtter.response = output
                #print meta_code
            else:
                output = "못찾겠네요"
                sdsUtter = self.sds_stub.FillSlots(sds_slots)
                sdsUtter.response = output
                print output

            elif or_add is not None and or_useradd is not None and or_drink is not None and or_name is not None and or_phone is not None:
                output = '잠시만 기다리시면 주문하신 메뉴를 신속히 배달해 드리겠습니다. 기다리시는 동안 재밌는 영상![END]'
                sds_slots.slots['output'] = output
                meta_code = '<!DOCTYPE html> <html> <head> </head> <body> <iframe width="330" height="200" src="https://www.youtube.com/embed/YwN-CN9EjTg" frameborder="0" allowfullscreen></iframe> </body> </html>'
                sdsUtter = self.sds_stub.FillSlots(sds_slots)
                sdsUtter.response = output
                print meta_code
                        # or_add의 변수를 받아서 해당 값을 지도로 검색하도록 한다.'''


        if dialog_act == 'inform' and or_title is not None:

            param = or_title.encode("utf-8")
            books = self.query_detail(client_id, client_secret, param, "title")
            if len(books) == 0:
                output = "검색결과가 없습니다 다시 검색해주세요"
                sds_slots.slots['user.title'] = None
            else:
                output = param + "에 대한 검색결과입니다. 처음으로 돌아가시려면 '뒤로'를 입력해주시기 바랍니다."
                result = ""
                meta_code = ""
                # book.Title() / book.Author() / book.ImageURL() / .Price() / .Publisher() / .Description() / .Link()
                book = books[0]

                result += "<table border='1'> <tbody> <tr> <th colspan='3'> " + book.Title()
                result += "</th> </tr> <tr> <td rowspan='4'> "
                result += "<img src = '" + book.ImageURL() + "'alt = 'file:wiki.png' title = 'file:wiki.png' width = '100px' / >"
                result += "</td> <td> " + book.Author() + " </td> </tr> <tr> <td> "
                result += book.Publisher() + " </td> </tr> <tr> <td> "
                result += "<a href= '" + book.Link() + "'>내용상세 </a>" + "</td> </tr> <tr> <td> "
                result += book.Price() + "<sub> 원 </sub> </td> </tr> <tr> <td colspan='3'> " + book.Description() + "</td> </tr> </tbody> </table>"

                # result += "</ul>"
                print "img :" + books[0].ImageURL()
                # result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
                # result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
                print "result : " + result
                meta_code += '<!DOCTYPE html> <html> <head> </head> <body>' + result + '</body> </html>'
            sdsUtter = self.sds_stub.FillSlots(sds_slots)
            sdsUtter.response = output
            on_title = None

        elif dialog_act == 'inform_search' and or_search is not None:
            start_point = 1
            param = or_search.encode("utf-8")
            books = self.query(client_id, client_secret, param, start_point)
            if len(books) == 0:
                output = "검색결과가 없습니다 다시 검색해주세요"
                sds_slots.slots['user.search'] = None
            else:
                output = param + "에 대한 검색결과입니다. 자세하게 알고싶은 책이 있으신가요?"
                result = "<ul>"
                meta_code = ""
                for book in books:
                    result += "<li><b>" + book.Title() + "</b>/<b>" + book.Author() + "</b></li></p>"
                result += "</ul>"
                print "img :" + books[0].ImageURL()
                # result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
                # result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
                print "result : " + result
                meta_code += '<!DOCTYPE html> <html> <head> </head> <body>' + result + '</body> </html>'
            sdsUtter = self.sds_stub.FillSlots(sds_slots)
            sdsUtter.response = output
            on_search = None

        elif dialog_act == 'select_from_list' and or_title is not None:
            print("select : ", or_title)
            param = or_title.encode("utf-8")
            books = self.query_detail(client_id, client_secret, param, "title")
            output = param + "에 대한 검색결과입니다."
            result = ""
            meta_code = ""
            # book.Title() / book.Author() / book.ImageURL() / .Price() / .Publisher() / .Description() / .Link()
            book = books[0]

            result += "<table border='1'> <tbody> <tr> <th colspan='3'> " + book.Title()
            result += "</th> </tr> <tr> <td rowspan='4'> "
            result += "<img src = '" + book.ImageURL() + "'alt = 'file:wiki.png' title = 'file:wiki.png' width = '100px' / >"
            result += "</td> <td> " + book.Author() + " </td> </tr> <tr> <td> "
            result += book.Publisher() + " </td> </tr> <tr> <td> "
            result += "<a href= '" + book.Link() + "'>내용상세 </a>" + "</td> </tr> <tr> <td> "
            result += book.Price() + "<sub> 원 </sub> </td> </tr> <tr> <td colspan='3'> " + book.Description() + "</td> </tr> </tbody> </table>"

            # result += "</ul>"
            print "img :" + books[0].ImageURL()
            # result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
            # result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
            print "result : " + result

            meta_code += '<!DOCTYPE html> <html> <head> </head> <body>' + result + '</body> </html>'
            sdsUtter = self.sds_stub.FillSlots(sds_slots)
            sdsUtter.response = output
            or_title = None

        elif dialog_act == 'best_seller':
            output = "요즘 핫하 책들이에요. 자세하게 알고싶은 책이 있으신가요?"
            result = "<ul>"
            meta_code = ""

            result += "<li><b>하이큐</b>/<b>하루다테 하루이치</b></li>"
            result += "<li><b>나의 문화유산답사기</b>/<b>유홍준</b></li>"
            result += "<li><b>살인자의 기억법</b>/<b>김영하</b></li>"
            result += "<li><b>82년생 김지영</b>/<b>조남주</b></li>"
            result += "<li><b>언어의 온도</b>/<b>이기주</b></li>"
            result += "</ul>"

            meta_code += '<!DOCTYPE html> <html> <head> </head> <body>' + result + '</body> </html>'
            sdsUtter = self.sds_stub.FillSlots(sds_slots)
            sdsUtter.response = output

        elif dialog_act == 'more_book' and or_search is not None:
            param = or_search.encode("utf-8")
            start_point += 5
            books = self.query(client_id, client_secret, param, start_point)
            if len(books) == 0:
                output = "이제 없어요"
                sds_slots.slots['user.search'] = None
            else:
                output = param + "에 대한 검색결과입니다. 자세하게 알고싶은 책이 있으신가요?"
                result = "<ul>"
                meta_code = ""
                for book in books:
                    result += "<li><b>" + book.Title() + "</b>/<b>" + book.Author() + "</b></li></p>"
                result += "</ul>"
                print "img :" + books[0].ImageURL()
                # result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
                # result += '<iframe width = "100" height = "100" src = '+books[0].ImageURL()+' frameborder = "0" allowfullscreen > < / iframe >'
                print "result : " + result
                meta_code += '<!DOCTYPE html> <html> <head> </head> <body>' + result + '</body> </html>'
            sdsUtter = self.sds_stub.FillSlots(sds_slots)
            sdsUtter.response = output
            on_search = None

        else:
            sdsUtter = self.sds_stub.FillSlots(sds_slots)


        print "[System output] " + sdsUtter.response

        talk_res = provider_pb2.TalkResponse()
        talk_res.text = sdsUtter.response
        print '< talk_res >', talk_res


        meta_data['out.embed.type'] = 'html5'
        meta_data['out.embed.data.body'] = meta_code  # 타입의 따른 내용 정의
        print '< meta_code > ', meta_code  # 메타데이터 링크에 대한 정보 출력

        print '----------------------- [TALK 끝] -------------------'

        if str(talk_res.text).count('[END]') != 0:                  #[END]가 있을 경우
            if or_add is not None and or_useradd is not None and or_drink is not None:          #or_add,or_useradd,or_drink의 값이 있을경우
                if or_sand is None:                                                                #or_sand의 값이 없을경우도 넣어준다.
                    or_sand = 'No Sand'

                print '[sds_act.filled_slots](address, user.address, user.drink, user.sandwich, or_name, or_phone)', or_add, or_useradd, or_drink, or_sand, or_name, or_phone
                # 각 슬롯변수를 합하기위한 변수설정
                cul1 = or_add + ' ' + or_useradd
                cul2 = or_drink + '/' + or_sand
                cul3 = or_name
                cul4 = or_phone
                print "cul1 : ", str(cul1), " cul2 : ", str(cul2), " cul3 : ", str(cul3), " cul4 : ", str(cul4)

                insert_query = "INSERT INTO " + self.db_table + " VALUES (%s,%s,%s,%s) "   #database에 값을 넣기위한 변수 설정  (문자열 네개로 삽입)

                curs.execute(insert_query, (str(cul1), str(cul2), str(cul3), str(cul4)))         #연동시킨 database의 table에 해당 값을 넣는다.

                conn.commit()

                text = "주소 : " + or_add + ' ' + or_useradd + ", 메뉴 : " + or_drink + '/' + or_sand + ", 이름 : " + or_name + ' ' + ", 연락처 : " + or_phone
                #해당 슬롯의 값을 텍스트로 정리
                sendMail(text)                  #텍스트를 함수를 이용하여 지정된 메일로 보낸다.

                meta_data['out.embed.type'] = 'html5'
                meta_data['out.embed.data.body'] = meta_code  # 타입의 따른 내용 정의
                talk_res.meta['out.embed.type'] = meta_data['out.embed.type']  # 추가적인 meta_data 타입 정의

            talk_res.state = provider_pb2.DIAG_CLOSED  # 대화 상태 종료로 인한 close
            self.sds_stub.Close(dsk)  # 위와 동일
            talk_res.text = talk_res.text[:-5]  # 최종 발화문전달
            print '< talk_res.talk >', talk_res.text
        else:
            pass

        curs.close()
        conn.close()

        talk_res.meta['out.embed.type'] = meta_data['out.embed.type']  # 추가적인 meta_data 타입 정의
        talk_res.meta['out.embed.data.body'] = meta_data['out.embed.data.body']
        return talk_res

    def Close(self, req, context):
       print 'Closing for ', req.session_id, req.agent_key
       talk_stat = provider_pb2.TalkStat()
       talk_stat.session_key = req.session_id
       talk_stat.agent_key = req.agent_key

       ses = sds_pb2.DialogueSessionKey()
       ses.session_key = req.session_id
       self.sds_stub.Close(ses)
       return talk_stat

def serve():
    parser = argparse.ArgumentParser(description='ordercof_simple_DA')
    parser.add_argument('-p', '--port',
                               nargs='?',
                               dest='port',
                               required=True,
                               type=int,
                               help='port to access server')
    args = parser.parse_args()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    provider_pb2.add_DialogAgentProviderServicer_to_server(ordercof_simple_DA(),
                                                                  server)

    listen = '[::]' + ':' + str(args.port)
    server.add_insecure_port(listen)

    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
            server.stop(0)

if __name__ == '__main__':
   serve()
        

