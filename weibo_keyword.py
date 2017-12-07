# -- coding: utf-8 -- –
import sys, getopt
import csv
import configparser
import mysql.connector
import datetime
from weibo_common import updateMysqlDB, queryOneMysqlDB

def appendDB(product_seg, circle, keyword):
    sql = 'INSERT INTO Weibo_keyword (product_seg, circle, keyword, create_at) VALUES ("{}", "{}", "{}", "{}")'.format(product_seg, circle, keyword, datetime.datetime.utcnow())
    updateMysqlDB(sql)

def checkExistDB(product_seg, circle, keyword):
    sql = 'SELECT * FROM Weibo_keyword WHERE product_seg="{}" AND circle="{}" AND keyword="{}"'.format(product_seg, circle, keyword)
    return queryOneMysqlDB(sql)

def csv2Db(filename):
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            searchResult = []
            for item in reader:
                product_seg = item[0].replace('\ufeff', '')
                circle = item[1]
                keyword = item[2]
                #print(repr("{}-{}-{}".format(product_seg, circle, keyword)))
                if checkExistDB(product_seg, circle, keyword) == None:
                    appendDB(product_seg, circle, keyword)
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(filename, reader.line_num, e))


def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hf:",["filename="])
    except getopt.GetoptError:
        print ('weibo_keyword.py -f <csv filename>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('weibo_keyword.py -f <filename>')
            sys.exit()
        elif opt in ('-f', '--filename'):
            filename = arg
            csv2Db(filename)

if __name__ == "__main__":
   main(sys.argv[1:])
