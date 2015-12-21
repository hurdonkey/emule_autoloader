#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
File: ed2k_autoload.py
Author: [Hurd]Donkey
Description: A script parse html dom and search ed2k links,
 then add emule task on web console.
'''


import os
import sys
import urllib
import urllib2
import bs4
import gzip
import StringIO
import re
import chardet


filecoding='utf-8'
syscoding=sys.getfilesystemencoding()


MULE_SERVER="192.168.137.102:4711"
MULE_PASSWD_ROOT="901104zhl"

global rexp_ed2khash
rexp_ed2khash=r'ed2k://\|file\|.*\|\d+\|(\w{32})\|(?:.*\|)?/'


def ungzip(data):
        fd_str=StringIO.StringIO(data)
        fd_gzip=gzip.GzipFile(fileobj=fd_str)
        html=fd_gzip.read()
        return html


def get_ed2k(url):
        """
        get ed2k links from html page
        url format: http://www.renrencd.com/view-219427.html
        """
        l_ed2k=[]

        try:
                conn=urllib.urlopen(url)
        except Exception:
                print "connect url failed!"
                exit(1)
        html=conn.read().decode('utf-8').encode(filecoding)
        conn.close()

        fd=open("ed2kpage.html", "w")
        fd.write(html)
        fd.close()

        dom=bs4.BeautifulSoup(html, "lxml")
        #dom=BeautifulSoup(conn, "lxml")
        l_soupitem=dom.find("table", attrs={"class": "ResListArea"}).find("tbody").findAll("tr", attrs={"class": "ResListCell"})
        for i in l_soupitem:       #-1: select and toolbar on last line
                try:
                        ed2k=i.find("td", attrs={"width":"700"}).find("a").get("href")
                except Exception:
                        #print "no find in this item"
                        continue
                #print ed2k
                #print repr(ed2k)
                #print repr(ed2k.encode(filecoding))
                ed2k=ed2k.encode(filecoding)
                l_ed2k.append(ed2k)
        return l_ed2k


def login():
        """
        login and get session
        url format: http://10.1.1.159:4711
        post data: {"p":<login password>, "w":"password"}
        """
        data={"p":MULE_PASSWD_ROOT, "w":"password"}
        params=urllib.urlencode(data)
        #print params
        try:
                conn=urllib.urlopen("http://%s/?%s" % (MULE_SERVER, params))
        except Exception:
                print "connect mule server failed"
                exit(1)
        html=conn.read()
        conn.close()

        dom=bs4.BeautifulSoup(html, "lxml")
        try:
                session=dom.find("form").find("input", attrs={"name": "ses"}).get("value")
        except Exception:
                print "logging password error!"
                return
        print "login success: %s" % session
        return session


def add_task(ed2k, session):
        """
        add aumle ed2k task on web console
        ed2k format: ed2k://|file|Mozilla%20Firefox%201.7.3%20[Multilenguage].rar|167927812|FE76D7B56B5E1E5800A7D5194B8C81D8|/
        url format: http://10.1.1.159:4711/?ses=-1085710356&w=transfer&ed2k=ed2k%3A%2F%2F%7Cfile%7CMozilla%2520Firefox%25201.7.3%2520%5BMultilenguage%5D.rar%7C167927812%7CFE76D7B56B5E1E5800A7D5194B8C81D8%7C%2F
        """
        data={"ses": session, "w": "transfer", "ed2k": ed2k}
        params=urllib.urlencode(data)
        #print params
        try:
                conn=urllib.urlopen("http://%s/?%s" % (MULE_SERVER, params))
        except Exception:
                print "connect mule server failed!"
                exit(1)
        html=conn.read()
        conn.close()
        print "add task success!"
        return True


def check_task(ed2k, session):
        """
        check added task
        url format: http://10.1.1.159:4711/?ses=-1085710356&w=transfer
        """
        data={"ses": session, "w": "transfer"}
        params=urllib.urlencode(data)
        #print params
        try:
                conn=urllib.urlopen("http://%s/?%s" % (MULE_SERVER, params))
        except Exception:
                print "connect mule server failed"
                exit(1)
        data=conn.read()
        content_encoding=conn.info().getheader("Content-Encoding")
        conn.close()
        #print context

        if content_encoding.find('gzip') > -1:
                html=ungzip(data)
        else:
                html = data

        fd=open("transfer.html", "w")
        fd.write(html)
        fd.close()

        recp_ed2khash=re.compile(rexp_ed2khash, re.I)

        ed2k+='/'
        #print ed2k
        ed2khash=recp_ed2khash.findall(ed2k)[0].upper()
        #print ed2khash
        if ed2khash == None:
                print "Error ed2k link!"
                exit(1)

        l_ret_ed2khash=recp_ed2khash.findall(html)
        #print len(l_ret_ed2khash)
        for i in l_ret_ed2khash:
                if i.upper() == ed2khash:
                        print "find this task success!"
                        return True
        print "find this task failed!"
        return False


def logout(session):
        """
        logout with session
        url format: http://10.1.1.159:4711/?ses=-1085710356&w=logout
        """
        data={"ses": session, "w": "logout"}
        params=urllib.urlencode(data)
        #print params
        try:
                conn=urllib.urlopen("http://%s/?%s" % (MULE_SERVER, params))
        except Exception:
                print "connect mule server failed!"
                exit(1)
        html=conn.read()
        conn.close()
        print "logout success: %s" % session
        return True


def main():
        print 'Filecoding: ', filecoding
        print 'Syscoding: ', syscoding

        if len(sys.argv) < 2:
                print "Useage: %s <url>" % sys.argv[0]
                return
        url=sys.argv[1]
        #print url

        session=login()
        #session="1956982249"

        l_ed2k=get_ed2k(url)
        #print len(l_ed2k)
        for i in l_ed2k:
                print "=== get ed2k link ==="
                print i
                add_task(i,session)
        #add_task(ed2k, session)

        for i in l_ed2k:
                print "=== find ed2k link ==="
                print i
                res=check_task(i, session)
        #res=check_task(ed2k, session)

        logout(session)


if __name__ == '__main__':
        main()
