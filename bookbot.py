import os
import sys
import xml.etree.ElementTree as ET
import urllib.request
client_id = "pQ9flPrSlR3iB2m7N0w4"
client_secret = "{password}"
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
    #print(response_body.decode('utf-8'))
    tree = ET.ElementTree(ET.fromstring(response_body.decode('utf-8')))
    root = tree.getroot()
    print(root.tag)
else:
    print("Error Code:" + rescode)