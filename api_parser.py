#-*- coding: utf-8 -*-

import books

def convertXMLtoObjects(root):
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


import os
import sys
import urllib
import xml.etree.ElementTree as ET
import urllib2
import requests
client_id = "pQ9flPrSlR3iB2m7N0w4"
client_secret = "M3Ziiv0li1"

def query(id, pw, params):
    encText = urllib.pathname2url(params)
    title = urllib.pathname2url(params)
    url = "https://openapi.naver.com/v1/search/book.xml?query=" + encText+"&display=10&start=1&sort=count"  # json 결과
    #url = "https://openapi.naver.com/v1/search/book_adv.xml?d_auth="+title+"&display=10&start=1"  # json 결과

    # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # xml 결과
    request = urllib2.Request(url)

    request.add_header("X-Naver-Client-Id",id)
    request.add_header("X-Naver-Client-Secret",pw)
    response = urllib2.urlopen(request)
    rescode = response.getcode()

    if(rescode==200):
        response_body = response.read()
        result = response_body.decode("utf-8").encode('utf-8')
        #print(result)
        #print(result)
        tree = ET.ElementTree(ET.fromstring(result))


        root = tree.getroot()
        book_ruslts = convertXMLtoObjects(root)
        for book in book_ruslts:
            print(book.Title())
            print(book.Description())
            print("\n")
        return book_ruslts

    else:
        print("Error Code:" + rescode)

def query_detail(id, pw, params, theme):
    param = urllib.pathname2url(params)
    url = ""
    if theme == "title":
        url = "https://openapi.naver.com/v1/search/book_adv.xml?d_titl="+param+"&display=10&start=1"  # json 결과
    elif theme == "author":
        url = "https://openapi.naver.com/v1/search/book_adv.xml?d_auth="+param+"&display=10&start=1&sort=count"  # json 결과
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
        book_ruslts = convertXMLtoObjects(root)
        for book in book_ruslts:
            print(book.Title())
            print(book.Description())
            print("\n")

    else:
        print("Error Code:" + rescode)

#query(client_id, client_secret, "여행")

query_detail(client_id, client_secret, "모든 요일의 여행", "title")