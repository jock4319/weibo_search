# -- coding: utf-8 -- –
import configparser
import mysql.connector
import time
from selenium import webdriver

config = configparser.ConfigParser()
config.read('config.ini')

def createMysqlDB():
    mysqlDB = mysql.connector.connect(host=config['MySQLDB']['HOST'],    # your host, usually localhost
                        port=config['MySQLDB']['PORT'],
                        user=config['MySQLDB']['USER'],         # your username
                        passwd=config['MySQLDB']['PASSWORD'],  # your password
                        db=config['MySQLDB']['DB'])        # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    return mysqlDB

def updateMysqlDB(sql):
    mysqlDB = createMysqlDB()
    dbCursor = mysqlDB.cursor()
    print(sql)
    try:
        dbCursor.execute(sql)
        mysqlDB.commit()
    except Exception as e:
        print(e)
        mysqlDB.rollback()
    mysqlDB.close()

def queryOneMysqlDB(sql):
    mysqlDB = createMysqlDB()
    dbCursor = mysqlDB.cursor()
    try:
        dbCursor.execute(sql)
        return dbCursor.fetchone()
    except Exception as e:
        print(e)
    return None

def queryAllMysqlDB(sql):
    mysqlDB = createMysqlDB()
    dbCursor = mysqlDB.cursor()
    try:
        dbCursor.execute(sql)
        return dbCursor.fetchall()
    except Exception as e:
        print(e)
    return None

def createBrowserChrome():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(60)
    return driver

def createBrowserFirefox():
    try:
        profile = webdriver.FirefoxProfile(config['Firefox']['PROFILE_OSX'])
    except:
        profile = webdriver.FirefoxProfile(config['Firefox']['PROFILE_WIN'])
    driver = webdriver.Firefox(profile)
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(60)
    return driver

def openUrlWithRetry(driver, url, retry):
    countRetry = retry
    while True:
        try:
            driver.get(url)
        except Exception as ex:
            print(ex)
            print("Timeout, retrying...")
            countRetry-=1
            if countRetry <= 0:
                print("Maximum number of retry reached")
                break
            time.sleep(5)
            continue
        else:
            break
    return countRetry
