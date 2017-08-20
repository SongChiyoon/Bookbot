import books

def convertXMLtoObjects(root):
    book_list = []
    for channel in root:
        for item in channel.findall('item'):
            book = books.books()
            if item.find('title') is not None:
                book.setTitle(item.find('title').text)
            if item.find('author') is not None:
                book.setAuthoor(item.find('author').text)
            if item.find('link') is not None:
                book.setLink(item.find('link').text)

            book_list.append(book)

    return book_list

import os
import sys
import xml.etree.ElementTree as ET
import urllib.request

client_id = "pQ9flPrSlR3iB2m7N0w4"
client_secret = "M3Ziiv0li1"
encText = urllib.parse.quote("소설")
url = "https://openapi.naver.com/v1/search/book.xml?query=" + encText +"&display=10&start=1" # json 결과
# url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # xml 결과
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request)
rescode = response.getcode()




if(rescode==200):
    response_body = response.read()
    result = response_body.decode('utf-8')
    #print(result)
    tree = ET.ElementTree(ET.fromstring(result))
    root = tree.getroot()
    books = convertXMLtoObjects(root)

    print("result : {}".format(books[0].Link()))

else:
    print("Error Code:" + rescode)

