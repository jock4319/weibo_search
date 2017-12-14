# -- coding: utf-8 -- –
import sys, getopt
import csv
import configparser
import mysql.connector
import datetime, time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote, urljoin
import re
from random import randint
from lxml import etree
from weibo_common import createBrowserFirefox, openUrlWithRetry, updateMysqlDB, queryOneMysqlDB

config = configparser.ConfigParser()
config.read('config.ini')
MIN_FANS = int(config['Property']['MIN_FANS'])

def searchUserCrawler(keyword, MAX_PAGE):
    listSearch = ["http://s.weibo.com/user/&tag=", "http://s.weibo.com/user/"]
    print('Keyword is %s, %d page(s)' % (keyword, MAX_PAGE))
    _page = 1

    driver = createBrowserFirefox()
    searchResult = []
    html = ''
    for search in listSearch:
        next_page = search + quote(quote(keyword))

        #while next_page:
        for _page in range(MAX_PAGE):
            for i in range(3):
                if openUrlWithRetry(driver, next_page, 5) <= 0:
                    break
                try:
                    time.sleep(2)
                    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pl_personlist"] | //div[@class="pl_noresult"]')))
                    #driver.execute_script("window.scrollTo(500, document.body.scrollHeight-500);")
                    driver.execute_script("window.scrollTo(500, 1000);")

                    htmlBody = driver.page_source
                    html = etree.HTML(htmlBody, base_url=driver.current_url)
                    break
                except:
                    driver.quit()
                    time.sleep(3)
                    driver = createBrowserFirefox()
            if html == '':
                print("Can't get html...")
                continue

            try:
                #personList = driver.find_elements_by_xpath('//div[@id="pl_user_feedList"]//div[@class="list_person clearfix"]')
                personList = html.xpath('//div[@id="pl_user_feedList"]//div[@class="list_person clearfix"]')
                if len(personList) == 0:
                    print("search no result")
                    break
            except NoSuchElementException:
                print("NoSuchElementException")
                break
            for person in personList:
                personInfo = []
                try:
                    #title = person.find_element_by_xpath('.//a[@class="W_texta W_fb"]').get_attribute('title')
                    title = person.xpath('.//a[@class="W_texta W_fb"]')[0].attrib['title']
                    print(title)
                    personInfo.append(title)
                except:
                    continue
                try:
                    #fans = person.find_elements_by_xpath('.//a[@class="W_linkb"]')[2].text.replace('万', '0000')
                    fans = person.xpath('.//a[@class="W_linkb"]')[2].text.replace('万', '0000')
                    print(fans)
                    #personInfo.append(int(fans))
                except:
                    #personInfo.append('')
                    pass

                # try:
                #     desc = person.find_element_by_xpath('.//p[@class="person_card"]').text
                #     print(desc)
                #     personInfo.append(desc)
                # except:
                #     personInfo.append('')
                #     pass
                try:
                    #link = person.find_elements_by_xpath('.//a[@class="W_linkb"]')[0].get_attribute('href').split('?')[0]
                    link = urljoin(driver.current_url, person.xpath('.//a[@class="W_linkb"]/@href')[0].split('?')[0]).replace('www.', '')
                    print(link)
                    personInfo.append(link)
                except:
                    personInfo.append('')
                    pass
                if int(fans) >= MIN_FANS:
                    already = 0
                    for res in searchResult:
                        if res[1] == personInfo[1]:
                            already = 1
                            break
                    if already == 0:
                        searchResult.append(personInfo)
                print("---- %d ----" % len(searchResult))

            nextPage = html.xpath('//a[text()="下一页"]/@href')
            if len(nextPage) > 0:
                next_page = urljoin(driver.current_url, nextPage[0])
                print(next_page)
            else:
                print ("No next page")
                break
    driver.quit()
    return searchResult

def searchCrawler(keyword, MAX_PAGE):
    print('Keyword is %s, %d page(s)' % (keyword, MAX_PAGE))
    _page = 1
    next_page = "http://s.weibo.com/weibo/" + quote(quote(keyword))

    driver = createBrowserFirefox()
    searchResult = []
    html = ''
    for _page in range(MAX_PAGE):
        for i in range(3):
            if openUrlWithRetry(driver, next_page, 3) <= 0:
                break
            try:
                time.sleep(2)
                element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@node-type="feed_list"]')))
                #driver.execute_script("window.scrollTo(500, document.body.scrollHeight-500);")
                driver.execute_script("window.scrollTo(500, 1000);")

                htmlBody = driver.page_source
                html = etree.HTML(htmlBody, base_url=driver.current_url)
                break
            except:
                driver.quit()
                time.sleep(3)
                driver = createBrowserFirefox()
        if html == '':
            print("Can't get html...")
            continue
        # star list
        try:
            #personList = driver.find_elements_by_xpath('//div[@class="list_star clearfix"]/div[@class="star_detail"]/p[@class="star_name"]/a[@class="name_txt"]')
            personList = html.xpath('//div[@class="list_star clearfix"]/div[@class="star_detail"]/p[@class="star_name"]/a[@class="name_txt"]')
            if len(personList) == 0:
                print("no result")
        except NoSuchElementException:
            print("NoSuchElementException")
            #return searchResult
        for person in personList:
            personInfo = []
            try:
                title = person.text.strip()
                #link = person.get_attribute('href').split('?')[0]
                link = urljoin(driver.current_url, person.attrib['href'].split('?')[0]).replace('www.', '')
                print(title + ": " + link)
                personInfo.append(title)
                personInfo.append(link)
            except:
                pass
            searchResult.append(personInfo)
            #writer.writerow(searchResult)
            print("---- %d ----" % len(searchResult))

        # feed list
        try:
            #personList = driver.find_elements_by_xpath('//div[@action-type="feed_list_item"]//div[contains(@class, "feed_content")]/a[1]')
            personList = html.xpath('//div[@action-type="feed_list_item"]//div[contains(@class, "feed_content")]/a[1]')
            if len(personList) == 0:
                print("no result")
        except NoSuchElementException:
            print("NoSuchElementException")
            #return searchResult
        for person in personList:
            personInfo = []
            try:
                title = person.text.strip()
                #link = person.get_attribute('href').split('?')[0]
                link = urljoin(driver.current_url, person.attrib['href'].split('?')[0]).replace('www.', '')
                print(title + ": " + link)
                personInfo.append(title)
                personInfo.append(link)
            except:
                pass
            searchResult.append(personInfo)
            #writer.writerow(searchResult)
            print("---- %d ----" % len(searchResult))

        nextPage = html.xpath('//a[text()="下一页"]/@href')
        if len(nextPage) > 0:
            next_page = urljoin(driver.current_url, nextPage[0])
            print(next_page)
        else:
            print ("No next page")
            break
    driver.quit()
    return searchResult

def searchFollowerCrawler(page_id, MAX_PAGE):
    print('Page id is %s, %d page(s)' % (page_id, MAX_PAGE))
    _page = 1
    next_page = "http://weibo.com/p/" + str(page_id) + "/follow?sudaref=weibo.com"

    driver = createBrowserFirefox()
    searchResult = []
    html = ''
    for _page in range(MAX_PAGE):
        for i in range(3):
            if openUrlWithRetry(driver, next_page, 3) <= 0:
                break
            try:
                time.sleep(5)
                element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@class="follow_inner"]/ul[@class="follow_list"]')))
                htmlBody = driver.find_element_by_tag_name('body').get_attribute('innerHTML')
                html = etree.HTML(htmlBody, base_url=driver.current_url)
                break
            except:
                driver.quit()
                time.sleep(3)
                driver = createBrowserFirefox()
        if html == '':
            print("Can't get html...")
            continue

        personList = html.xpath('//div[@class="follow_inner"]/ul[@class="follow_list"]/li')
        for person in personList:
            try:
                fans = int(person.xpath('.//div[@class="info_connect"]/span[2]/em/a')[0].text)
            except:
                fans = 0
            print('fans: {}'.format(fans))
            if fans >= MIN_FANS:
                ele = person.xpath('.//div[contains(@class, "info_name")]/a[1]')[0]
                title = ele.text.strip()
                link = urljoin(driver.current_url, ele.attrib['href'].split('?')[0]).replace('www.', '')
                print(title + ": " + link)
                searchResult.append([title, link])

            print("---- %d ----" % len(searchResult))

        #nextPage = html.xpath('//span[text()="下一页"]')[0].xpath('../a/@href')
        nextPage = html.xpath('//a[contains(@class, "page next")]/@href')
        if len(nextPage) > 0:
            next_page = urljoin(driver.current_url, nextPage[0])
            print(next_page)
        else:
            print ("No next page")
            break
    driver.quit()
    return searchResult

def queryKeywordMysqlDB():
    sql = 'SELECT id, keyword FROM Weibo_keyword WHERE finished != 1 LIMIT 1'
    return queryOneMysqlDB(sql)

def checkListMysqlDB(keyword_id, influencer, link):
    sql = 'SELECT circle FROM Weibo_keyword WHERE id="{}"'.format(keyword_id)
    circle = queryOneMysqlDB(sql)[0]
    #sql = 'SELECT keyword_id, influencer, link FROM Weibo WHERE keyword_id="{}" AND influencer="{}" AND link="{}"'.format(keyword_id, influencer, link)
    sql = 'SELECT r.id FROM Weibo AS r, Weibo_keyword AS k WHERE r.keyword_id=k.id AND r.influencer="{}" AND r.link="{}" AND k.circle="{}"'.format(influencer, link, circle)
    return queryOneMysqlDB(sql)

def appendMysqlDB(keyword_id, influencer, link):
    sql = 'INSERT INTO Weibo (keyword_id, influencer, link) VALUES ("{}", "{}", "{}")'.format(keyword_id, influencer, link)
    updateMysqlDB(sql)

def markAsFinishedMysqlDB(keyword_id, keyword):
    sql = 'UPDATE Weibo_keyword SET finished=1 WHERE id="{}" AND keyword="{}"'.format(keyword_id, keyword)
    updateMysqlDB(sql)

def queryPageidMysqlDB():
    sql = 'SELECT keyword_id, page_id FROM Weibo_page LIMIT 1'
    return queryOneMysqlDB(sql)

def delPageidMysqlDB(keyword_id, page_id):
    sql = 'DELETE FROM Weibo_page WHERE keyword_id="{}" AND page_id="{}"'.format(keyword_id, page_id)
    updateMysqlDB(sql)

def main(argv):
    MAX_PAGE = int(config['Property']['MAX_PAGE'])

    while True:
        while True:
            # search for follow
            pageId = queryPageidMysqlDB()
            if pageId == None:
                break

            print('-------- {}.{} --------'.format(pageId[0], pageId[1]))
            personList = searchFollowerCrawler(pageId[1], 5)    # only 5 pages available
            for person in personList:
                if checkListMysqlDB(pageId[0], person[0], person[1]) == None:
                    appendMysqlDB(pageId[0], person[0], person[1])

            delPageidMysqlDB(pageId[0], pageId[1])

        # search for keyword
        keyword = queryKeywordMysqlDB()
        if keyword == None:
            break

        print('-------- {}.{} --------'.format(keyword[0], keyword[1]))
        personList = searchUserCrawler(keyword[1], MAX_PAGE)
        for person in personList:
            if checkListMysqlDB(keyword[0], person[0], person[1]) == None:
                appendMysqlDB(keyword[0], person[0], person[1])

        time.sleep(randint(5,10))

        personList = searchCrawler(keyword[1], MAX_PAGE)
        for person in personList:
            if checkListMysqlDB(keyword[0], person[0], person[1]) == None:
                appendMysqlDB(keyword[0], person[0], person[1])

        markAsFinishedMysqlDB(keyword[0], keyword[1])

        time.sleep(randint(5,10))

if __name__ == "__main__":
   main(sys.argv[1:])
