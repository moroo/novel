#!/usr/bin/python3
"""
https://qiita.com/cupnoodlegirl/items/e20f353b5c369de1f5ed
https://info.finance.yahoo.co.jp/history/?code=1301.T&sy=1983&sm=4&sd=24&ey=2020&em=5&ed=24&tm=d
https://info.finance.yahoo.co.jp/history/?code=1301.T&sy=1983&sm=4&sd=24&ey=2020&em=5&ed=24&tm=d&p=2
Disabled http://kabusapo.com/dl-file/dl-stocklist.php
https://stockdatacenter.com/stockdata/companylist.csv
"""
import urllib.parse
import urllib.request
import io
import re
import codecs
import csv
import os
import time
import json
import datetime
import argparse

FINISHNOVEL="FINISHED"
NONOVEL="NONOVEL"

def send(ncode,args):
    """send query to yahoo api"""
    url = 'https://ncode.syosetu.com/novelview/infotop/ncode/{}/'.format(ncode)
    if args.verbose > 2:
        print(url)
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError:
        return NONOVEL
    data = response.read().decode('utf-8')
    if args.verbose > 5:
        print(data)
    return data

def novelstatus(data,args):
    updatere=re.compile("<th>最新部分掲載日</th>\n<td>(\d+)年 (\d+)月(\d+)日")
    t=data.find('<span id="noveltype">完結済')
    if t > 0:
        return FINISHNOVEL
    else:
        ut = updatere.search(data)
        if ut:
            lastupdate = datetime.date(int(ut.group(1)),int(ut.group(2)),int(ut.group(3)))
            return (datetime.date.today() - lastupdate).days

def checknovelstatus(args):
    novelstatuslist=[]
    if os.path.exists(args.codefile):
        with codecs.open(args.codefile,encoding='utf-8') as codefp:
            for line in codefp:
                ncode,title=line.strip().split(" ",maxsplit=1)
                if args.verbose > 2:
                    print(ncode,title)
                data = send(ncode,args)
                if data == NONOVEL:
                    novelstatuslist.append([ncode,title,NONOVEL])
                    if args.verbose > 2:
                        print("No Novel")
                else:
                    update = novelstatus(data,args)
                    if args.verbose > 2:
                        print(update)
                    novelstatuslist.append([ncode,title,update])
    else:
        data = send(args.codefile,args)
        if data == NONOVEL:
            print("No Novel")
            return
        update = novelstatus(data,args)
        print(update)
    return(novelstatuslist)

def makenovelfile(args):
    novelstatuslist = checknovelstatus(args)
    finishfp  = open(os.path.join(args.datadir,"finishlist.txt"),"w")
    nonovelfp  = open(os.path.join(args.datadir,"nonovellist.txt"),"w")
    overyearfp  = open(os.path.join(args.datadir,"overyearlist.txt"),"w")
    overmonthfp  = open(os.path.join(args.datadir,"overmonthlist.txt"),"w")
    novelfp  = open(os.path.join(args.datadir,"novellist.txt"),"w")
    for d in novelstatuslist:
        if d[2] == FINISHNOVEL:
            finishfp.write("{} {}\n".format(d[0],d[1]))
        elif d[2] == NONOVEL:
            nonovelfp.write("{} {}\n".format(d[0],d[1]))
        elif d[2] > 365:
            overyearfp.write("{} {}\n".format(d[0],d[1]))
        elif d[2] > 30:
            overmonthfp.write("{} {}\n".format(d[0],d[1]))
        else:
            novelfp.write("{} {}\n".format(d[0],d[1]))
    novelfp.close()
    overmonthfp.close()
    overyearfp.close()
    nonovelfp.close()
    finishfp.close()
    
if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Conjuction yahoo stock.\n create retrycode file to reget")
    ap.add_argument("-v","--verbose",help="vorbose",action="count", default=0)
    ap.add_argument("-c","--codefile",help="get stock code list file default:%(default)s",default="ncodefile.csv")
    ap.add_argument("-d","--datadir",help="store data dir default:%(default)s",default="data")
    args=ap.parse_args()
    if args.verbose > 0:
        print(args)
    #send("n4830bu",args)
    makenovelfile(args)


