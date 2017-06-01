#!/usr/bin/env python3
#-*- coding=utf-8 -*-
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
def get_news(topic, lang, number):
    res = urlopen("https://news.google.com/news/section?cf=all&topic="+topic+"&ned="+lang+"&ict=ln")
    soup = BeautifulSoup(res, "html.parser")
    #print soup.select(".esc-body")

    count = 1
    list_news =[]
    for item in soup.select(".esc-body"):
        content =''
        content += '======['+ str(count) +']=========\n'
        news_title = item.select(".esc-lead-article-title")[0].text
        news_url = item.select(".esc-lead-article-title")[0].find('a')['href']
        content += news_title + '\n'
        content += news_url +'\n'
        count += 1
        list_news.append(content)
        if count == number+1:
            break
    return list_news

def query_news(q, number):
    res = urlopen('https://news.google.com/news?q='+urllib.parse.quote(q))
    
    soup = BeautifulSoup(res, "html.parser")
    #print soup.select(".esc-body")
    #number=5
    count = 1
    list_news =[]
    for item in soup.select(".esc-body"):
        content =''
        content += '======['+ str(count) +']=========\n'
        news_title = item.select(".esc-lead-article-title")[0].text
        news_url = item.select(".esc-lead-article-title")[0].find('a')['href']
        content += news_title + '\n'
        content += news_url +'\n'
        count += 1
        list_news.append(content)
        if count == number+1:
            break
    return list_news

