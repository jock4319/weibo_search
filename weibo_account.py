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
from weibo_common import createBrowserFirefox, openUrlWithRetry, updateMysqlDB, queryOneMysqlDB, queryAllMysqlDB

config = configparser.ConfigParser()
config.read('config.ini')
MIN_FANS = int(config['Property']['MIN_FANS'])
DEFAULT_DATE = datetime.datetime(2000, 1, 1)

def personCrawler(keywordId, url, keywordList):
    PAGE = 2
    listQuery = ['?profile_ftype=1&is_all=1#_0', '?profile_ftype=1&is_ori=1#_0', \
        '?is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&page=2#feedtop', \
        '?is_search=0&visible=0&is_ori=1&is_tag=0&profile_ftype=1&page=2#feedtop']
    fans = 0
    description = ''
    avgForward = [0, 0, 0] # all, original, original with Keyword
    avgComment = [0, 0, 0]
    resForward = ['', '', ''] # all, original, original with Keyword
    resComment = ['', '', '']
    forward = [[], [], []] # all, original, original with Keyword
    comment = [[], [], []]
    lastPostTime = [DEFAULT_DATE, DEFAULT_DATE]
    postType = [0, 0, 0, 0]     # 'others', 'picture', 'video', 'article'
    listArticleRead = []
    resArticleRead = ''
    listContent = []
    countContent = 0
    ratioContent = ''
    listMention = []
    pageId = ''

    driver = createBrowserFirefox()
    html = ''

    for page in range(PAGE):

        for idx in range(PAGE):

            pageLoaded = 0
            for j in range(3):
                if openUrlWithRetry(driver, url + listQuery[page*2+idx], 5) > 0:
                    print(url)
                    time.sleep(randint(5,8))
                else:
                    break
                for i in range(20):
                    print("waiting for page load...")
                    try:
                        wait = WebDriverWait(driver, 10)
                        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="W_pages"] | //div[@class="WB_empty"] | //div[contains(@class, "WB_cardwrap")]')))
                        pageLoaded = 1
                        break
                    except:
                        pass
                    try:
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    except:
                        break
                if pageLoaded == 1:
                    try:
                        time.sleep(5)
                        #htmlBody = driver.page_source
                        htmlBody = driver.find_element_by_tag_name('body').get_attribute('innerHTML')
                        html = etree.HTML(htmlBody, base_url=driver.current_url)
                        break
                    except:
                        print("Closing browser and try again...")
                        driver.quit()
                        time.sleep(3)
                        driver = createBrowserFirefox()
                else:
                    print("Closing browser and try again...")
                    driver.quit()
                    time.sleep(3)
                    driver = createBrowserFirefox()
            if pageLoaded == 0:
                driver.quit()
                return fans, description, avgForward, avgComment, resForward, resComment, lastPostTime, postType, resArticleRead, countContent, pageId

            if page == 0 and idx == 0:
                try:
                    #title = driver.find_element_by_xpath('//div[@class="pf_username"]/h1').text
                    title = html.xpath('//div[@class="pf_username"]/h1')[0].text
                    print(title)
                except Exception as ex:
                    print(ex)
                try:
                    #description = driver.find_element_by_xpath('//div[@class="pf_intro"]').text
                    description = html.xpath('//div[@class="pf_intro"]')[0].text.strip()
                    print(description)
                except Exception as ex:
                    print(ex)
                try:
                    #fans = driver.find_element_by_xpath('//table[@class="tb_counter"]//span[text()="粉丝"]').find_element_by_xpath('../strong').text
                    fans = html.xpath('//table[@class="tb_counter"]//span[text()="粉丝"]')[0].xpath('../strong')[0].text
                    print(fans + "粉丝")
                    fans = int(fans)
                    if fans < MIN_FANS:
                        driver.quit()
                        return fans, description, avgForward, avgComment, resForward, resComment, lastPostTime, postType, resArticleRead, countContent, pageId
                except Exception as ex:
                    fans = 0
                    print(ex)
                try:
                    pageId = html.xpath('//td[contains(@class, "current")]/a[@class="tab_link"]/@href')[0]
                    p2 = pageId.find("p/") + len("p/")
                    p3 = pageId.find("/", p2)
                    pageId = pageId[p2: p3]
                    print("page id: {}".format(pageId))
                except Exception as ex:
                    pageId = ''
                    print(ex)
                # try:
                #     description = driver.find_element_by_xpath('//div[@class="PCD_person_info"]/div/p[@class="info"]').text
                #     print(description)
                # except Exception as ex:
                #     print(ex)
            try:
                #cardList = driver.find_elements_by_xpath('//div[@node-type="feed_list"]/div[@action-type="feed_list_item"]')
                cardList = html.xpath('//div[@node-type="feed_list"]/div[@action-type="feed_list_item"]')
            except NoSuchElementException:
                print("NoSuchElementException")

            for card in cardList:
                # check if this is liked post
                try:
                    #print("xxxxx %d" % len(card.xpath('./div/h4[@class="obj_name S_txt2"]')))
                    #card.find_element_by_xpath('./div/h4[@class="obj_name S_txt2"]')
                    if len(card.xpath('./div/h4[@class="obj_name S_txt2"]')) > 0:
                        print("This is liked post, skip...")
                        listMention.append(card.xpath('./div[@node-type="feed_content"]//div[@class="WB_info"]/a')[0])
                        continue
                except:
                    pass
                # check if this is system post for birthday
                try:
                    #print("xxxxx %d" % len(card.xpath('.//a[@action-type="app_source"]')))
                    #if card.find_element_by_xpath('.//a[@action-type="app_source"]').text == '生日动态':
                    if card.xpath('.//a[@action-type="app_source"]')[0].text == '生日动态':
                        print("This is birthday post, skip...")
                        continue
                except:
                    pass
                # get post date
                try:
                    # element = card.find_element_by_xpath('.//a[@node-type="feed_list_item_date"]')
                    # driver.execute_script("arguments[0].scrollIntoView();", element)
                    # strPostTime = element.get_attribute('title')
                    strPostTime = card.xpath('.//a[@node-type="feed_list_item_date"]')[0].attrib['title']
                    postTime = datetime.datetime.strptime(strPostTime, '%Y-%m-%d %H:%M')
                    #print("%s == %s" % (strPostTime, postTime))
                except:
                    postTime = DEFAULT_DATE
                    print("Fail to get post time")

                # check the type of post
                if idx == 1:

                    cardType = 0    # 'others'
                    try:
                        #mediaBox = card.find_element_by_xpath('.//div[@class="media_box"]')
                        mediaBox = card.xpath('.//div[@class="media_box"]')[0]
                    except Exception as ex:
                        print(ex)
                        print('No media box')
                        mediaBox = None
                    try:
                        #if mediaBox.find_elements_by_xpath('./ul/li[@action-type="fl_pics"]'):
                        if len(mediaBox.xpath('./ul/li[@action-type="fl_pics"]')) > 0:
                            cardType = 1    # 'picture'
                    except:
                        pass
                    try:
                        #if mediaBox.find_elements_by_xpath('./ul/li[@node-type="fl_h5_video"]'):
                        if len(mediaBox.xpath('./ul/li[@node-type="fl_h5_video"]')) > 0:
                            cardType = 2    # 'video'
                    except:
                        pass
                    try:
                        #if mediaBox.find_elements_by_xpath('./div[@action-type="widget_articleLayer"]'):
                        if len(mediaBox.xpath('./div[@action-type="widget_articleLayer"]')) > 0:
                            cardType = 3    # 'article'
                            #mediaBox.find_element_by_xpath('./div[@action-type="widget_articleLayer"]/div[1]/div').click()
                            tree = html.getroottree()
                            print(tree.getpath(mediaBox.xpath('./div[@action-type="widget_articleLayer"]')[0]))
                            driver.find_element_by_xpath(tree.getpath(mediaBox.xpath('./div[@action-type="widget_articleLayer"]')[0])).click()

                            # get view number of article
                            #iframe = driver.find_element_by_xpath('//iframe[contains(@name, "articleLayer")]')
                            iframe = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//iframe[contains(@name, "articleLayer")]')))
                            driver.switch_to_frame(iframe)
                            #author = driver.find_element_by_xpath('//div[contains(@class, "authorinfo")]/div/span/a').get_attribute('href')
                            author = driver.find_element_by_xpath('//div[contains(@class, "authorinfo")]/div/span/a').text
                            print('author: %s' % author)
                            #if url == author:
                            if title == author:
                                read = driver.find_element_by_xpath('//div[contains(@class, "authorinfo")]/div[@class="W_fr"]/span[@class="num"]').text
                                read.replace('万', '0000')
                                read = re.sub("[^0123456789\.]", '', read)
                                listArticleRead.append(int(read))
                                print('read: %s' % read)
                            time.sleep(1)
                            driver.find_element_by_xpath('//div[@node-type="sidebar"]/a[1]').click()
                            driver.switch_to_default_content()
                    except Exception as ex:
                        print(ex)
                    postType[cardType] += 1
                    print('type: %d' % cardType)

                # get forward number
                try:
                    #forwardNum = card.find_element_by_xpath('.//span[@node-type="forward_btn_text"]//em[2]').text
                    forwardNum = card.xpath('.//span[@node-type="forward_btn_text"]//em[2]')[0].text
                    print(forwardNum)
                    forward[idx].append(int(forwardNum))
                except:
                    forward[idx].append(0)
                # get comment number
                try:
                    #commentNum = card.find_element_by_xpath('.//span[@node-type="comment_btn_text"]//em[2]').text
                    commentNum = card.xpath('.//span[@node-type="comment_btn_text"]//em[2]')[0].text
                    print(commentNum)
                    comment[idx].append(int(commentNum))
                except:
                    comment[idx].append(0)

                if postTime > lastPostTime[idx]:
                    lastPostTime[idx] = postTime
                else:
                    print("%s > %s" % (lastPostTime[idx], postTime))

            # gather all text content
            if idx == 1:
                try:
                    #listContent += (driver.find_elements_by_xpath('//div[@node-type="feed_list_content"]'))
                    listContent += (html.xpath('//div[@node-type="feed_list_content"]'))
                except Exception as ex:
                    print(ex)

                listMention += html.xpath('//a[contains(@usercard,"name=")]')
                listMention += html.xpath('//a[@node-type="feed_list_originNick"]')

    print("--- post type: %d-%d-%d-%d" % (postType[1], postType[2], postType[3], postType[0]))

    print("{}-{}-{}".format(len(forward[1]), len(comment[1]), len(listContent)))
    for idx in range(len(listContent)):
        contentText = "".join(listContent[idx].itertext()).lower()
        foundKeyword = False
        for keyword in keywordList:
            if keyword[0].lower() in contentText:
                countContent += 1
                print(listContent[idx].text.strip())
                foundKeyword = True
                break
        if foundKeyword:
            forward[2].append(forward[1][idx])
            comment[2].append(comment[1][idx])

    # calculate forward and comment number
    for idx in range(len(forward)):
        if len(forward[idx]) > 0:
            avgForward[idx] = round(sum(forward[idx]) / float(len(forward[idx])))
            resForward[idx] = ("%d~%d" % (min(forward[idx]), max(forward[idx])))
        else:
            print("No forward")
            avgForward[idx] = 0
            resForward[idx] = ("-")

        if len(comment[idx]) > 0:
            avgComment[idx] = round(sum(comment[idx]) / float(len(comment[idx])))
            resComment[idx] = ("%d~%d" % (min(comment[idx]), max(comment[idx])))
        else:
            print("No comment")
            avgComment[idx] = 0
            resComment[idx] = ("-")
        print("--- Average: %d, %d, count: %d, %d" % (round(avgForward[idx]), round(avgComment[idx]), len(forward[idx]), len(comment[idx])))
        print("    %s, %d" % (resForward[idx], avgForward[idx]))
        print("    %s, %d" % (resComment[idx], avgComment[idx]))

    # calculate 原創文章閱讀量（全range,均數)
    avgRead = 0
    if len(listArticleRead) > 0:
        for read in listArticleRead:
            avgRead += read
        avgRead = avgRead/len(listArticleRead)
        resArticleRead = ("%d~%d, %d" % (min(listArticleRead), max(listArticleRead), avgRead))
    else:
        resArticleRead = ("-")
    print("--- article read: %s" % resArticleRead)

    ratioContent = ('=(%d/%d)' % (countContent, len(listContent)))
    print("--- relate to keyword: %s" % ratioContent)

    mentions = []
    for mention in listMention:
        title = mention.text.strip()[1:]
        link = urljoin(driver.current_url, mention.attrib['href'].split('?')[0])
        if [title, link] not in mentions:
            mentions.append([title, link])
            #print(title + ": " + link)
            if CheckListMysqlDB(keywordId, title, link) == None:
                appendMysqlDB(keywordId, title, link)

    driver.quit()
    return fans, description, avgForward, avgComment, resForward, resComment, lastPostTime, postType, resArticleRead, countContent, pageId

def CheckListMysqlDB(keyword_id, influencer, link):
    sql = 'SELECT circle FROM Weibo_keyword WHERE id="{}"'.format(keyword_id)
    circle = queryOneMysqlDB(sql)[0]
    #sql = 'SELECT keyword_id, influencer, link FROM Weibo WHERE keyword_id="{}" AND influencer="{}" AND link="{}"'.format(keyword_id, influencer, link)
    sql = 'SELECT r.id FROM Weibo AS r, Weibo_keyword AS k WHERE r.keyword_id=k.id AND r.influencer="{}" AND r.link="{}" AND k.circle="{}"'.format(influencer, link, circle)
    return queryOneMysqlDB(sql)

def appendMysqlDB(keyword_id, influencer, link):
    sql = 'INSERT INTO Weibo (keyword_id, influencer, link) VALUES ("{}", "{}", "{}")'.format(keyword_id, influencer, link)
    updateMysqlDB(sql)

def queryAccountMysqlDB():
    sql = 'SELECT keyword_id, link FROM Weibo WHERE share_avg=0 AND comment_avg=0 AND post_type="" AND keyword_id!=0 LIMIT 1'
    return queryOneMysqlDB(sql)

def queryCircleMysqlDB(keyword_id):
    sql = 'SELECT circle FROM Weibo_keyword WHERE id="{}"'.format(keyword_id)
    return queryOneMysqlDB(sql)

def queryKeywordMysqlDB(circle):
    sql = 'SELECT keyword FROM Weibo_keyword WHERE circle="{}"'.format(circle)
    return queryAllMysqlDB(sql)

def appendPageidMysqlDB(keywordId, pageId):
    sql = 'INSERT INTO Weibo_page (keyword_id, page_id) VALUES ("{}", "{}")'.format(keywordId, pageId)
    updateMysqlDB(sql)

def delAccountMysqlDB(link):
    sql = 'DELETE FROM Weibo WHERE link="{}"'.format(link)
    updateMysqlDB(sql)

def main(argv):

    while True:
        account = queryAccountMysqlDB()
        if account == None:
            break

        try:
            keywordList = queryKeywordMysqlDB(queryCircleMysqlDB(account[0])[0])
        except:
            keywordList = [account[2]]
        print(keywordList)

        fans, description, avgForward, avgComment, resForward, resComment, lastPostTime, postType, resArticleRead, countContent, pageId = personCrawler(account[0], account[1], keywordList)
        if fans < MIN_FANS:
            delAccountMysqlDB(account[1])
            continue

        postType = ("%d-%d-%d-%d" % (postType[1], postType[2], postType[3], postType[0]))
        offcial = (1 if "官方" in description or "有限公司" in description else 0)
        sql = 'UPDATE Weibo SET follower="{}", share_avg="{}", comment_avg="{}", share_range="{}", comment_range="{}", lastPostTime="{}", \
            ori_share_avg="{}", ori_comment_avg="{}", ori_share_range="{}", ori_comment_range="{}", ori_lastPostTime="{}", \
            key_share_avg="{}", key_comment_avg="{}", key_share_range="{}", key_comment_range="{}", \
            post_type="{}", description="{}", article_read="{}", key_content="{}", official="{}", update_time="{}" WHERE keyword_id="{}" AND link="{}"'\
            .format(str(fans), str(avgForward[0]), str(avgComment[0]), resForward[0], resComment[0], (str(lastPostTime[0]) if lastPostTime[0] != DEFAULT_DATE else ''), \
            str(avgForward[1]), str(avgComment[1]), resForward[1], resComment[1], (str(lastPostTime[1]) if lastPostTime[1] != DEFAULT_DATE else ''), \
            str(avgForward[2]), str(avgComment[2]), resForward[2], resComment[2], \
            postType, description, resArticleRead, countContent, offcial, datetime.datetime.utcnow(), account[0], account[1])
        updateMysqlDB(sql)

        if avgForward[1] >= 10 or avgComment[1] >= 10:
            appendPageidMysqlDB(account[0], pageId)

if __name__ == "__main__":
   main(sys.argv[1:])
