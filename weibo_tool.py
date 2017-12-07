# -- coding: utf-8 -- –
import os, sys, getopt
import mysql.connector
import time
from weibo_common import updateMysqlDB, queryOneMysqlDB, queryAllMysqlDB

def addKeywordId():
    sql = "SELECT * FROM Weibo_keyword"
    keywordList = queryAllMysqlDB(sql)

    id = 0
    while True:
        sql = 'SELECT id, product_seg, circle, keyword FROM Weibo WHERE keyword_id=0 and id>"{}" LIMIT 1'.format(id)
        result = queryOneMysqlDB(sql)
        if result == None:
            break
        id = result[0]
        print("{} {} {} {}".format(result[0], result[1], result[2], result[3]))
        for keyword in keywordList:
            if result[1] == keyword[1] and result[2] == keyword[2] and result[3] == keyword[3]:
                sql = 'UPDATE Weibo SET keyword_id="{}" WHERE id="{}"'.format(keyword[0], result[0])
                updateMysqlDB(sql)
                break
        time.sleep(0.1)

def keyContent():
    sql = "SELECT id, ratio_content FROM Weibo"
    itemList = queryAllMysqlDB(sql)

    for item in itemList:
        if item[1] != '':
            p2 = item[1].find("=(") + len("=(")
            p3 = item[1].find("/", p2)
            keyContent = item[1][p2: p3]
            sql = 'UPDATE Weibo SET key_content="{}" WHERE id="{}"'.format(keyContent, item[0])
            updateMysqlDB(sql)

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hab")
    except getopt.GetoptError:
        print ('weibo_keyword.py -f -a -b')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('weibo_keyword.py -a -b')
            sys.exit()
        elif opt in ('-a', '--add_keyword_id'):
            addKeywordId()
        elif opt in ('-b', '--add_key_content'):
            keyContent()

if __name__ == "__main__":
   main(sys.argv[1:])
