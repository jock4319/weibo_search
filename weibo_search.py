#!/usr/bin/python
# -- coding: utf-8 -- –
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from pyvirtualdisplay import Display
import datetime, time, codecs, csv, os
import sys, getopt
from urllib.parse import quote
import re
from random import randint
#from UnicodeSupportForCsv import UnicodeReader, UnicodeWriter

DEFAULT_DATE = datetime.datetime(2000, 1, 1)

def createBrowser():
    uaList = open("useragent.txt")
    with uaList as f:
        ua = f.readlines()
    uaList.close()
    userAgent = random.choice(ua)
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override",userAgent.strip())
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.dir", "/var/www/html/amazon/vendor/excel/")
    profile.set_preference("browser.helperApps.neverAsk.openFile","text/csv,application/x-msexcel,application/excel,application/x-excel,application/vnd.ms-excel,text/html,text/plain,application/msword,application/xml")
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv,application/x-msexcel,application/excel,application/x-excel,application/vnd.ms-excel,text/html,text/plain,application/msword,application/xml")
    #profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "txt/csv,text/comma-separated-values,application/csv,application/msexcel,application/octet-stream")
    #profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,txt/csv,application/excel,text/comma-separated-values,application/csv")
    driver = webdriver.Firefox(profile)
    driver.implicitly_wait(10)
    return driver

def createBrowserChrome():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(60)
    return driver

def createBrowserFirefox():
    try:
        profile = webdriver.FirefoxProfile('/Users/jockchang/Library/Application Support/Firefox/Profiles/mkn50r8u.default')
    except:
        profile = webdriver.FirefoxProfile('C:\\Users\\jock.chang\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\31whtj8k.default-1510102946417')
    driver = webdriver.Firefox(profile)
    driver.implicitly_wait(10)
    driver.set_page_load_timeout(60)
    return driver

def searchUserCrawler(driver, keyword, MAX_PAGE):
    listSearch = ["http://s.weibo.com/user/&tag=", "http://s.weibo.com/user/"]
    print('Keyword is %s, %d page(s)' % (keyword, MAX_PAGE))
    _page = 1
    #next_page = "http://s.weibo.com/user/" + quote(quote(keyword)) + "&Refer=weibo_user"
    #next_page = "http://s.weibo.com/user/" + keyword + "&Refer=weibo_user"

    searchResult = []
    for search in listSearch:
        next_page = search + quote(quote(keyword))

        if openUrlWithRetry(driver, next_page, 5) <= 0:
            return searchResult
        while next_page:
            time.sleep(randint(5,15))
            # element = WebDriverWait(driver, 30).until(
            #     EC.presence_of_element_located((By.XPATH, "//div[@id='pl_user_feedList']"))
            #     )
            #driver.execute_script("window.scrollTo(500, document.body.scrollHeight-500);")
            driver.execute_script("window.scrollTo(500, 1000);")

            try:
                personList = driver.find_elements_by_xpath('//div[@id="pl_user_feedList"]//div[@class="list_person clearfix"]')
            except NoSuchElementException:
                print("NoSuchElementException")
                return searchResult
            for person in personList:
                personInfo = []
                try:
                    title = person.find_element_by_xpath('.//a[@class="W_texta W_fb"]').get_attribute('title')
                    print(title)
                    personInfo.append(title)
                except:
                    continue
                try:
                    fans = person.find_elements_by_xpath('.//a[@class="W_linkb"]')[2].text.replace('万', '0000')
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
                    link = person.find_elements_by_xpath('.//a[@class="W_linkb"]')[0].get_attribute('href').split('?')[0]
                    print(link)
                    personInfo.append(link)
                except:
                    personInfo.append('')
                    pass
                if int(fans) >= 10000:
                    already = 0
                    for res in searchResult:
                        if res[1] == personInfo[1]:
                            already = 1
                            break
                    if already == 0:
                        searchResult.append(personInfo)
                print("---- %d ----" % len(searchResult))

            if _page < MAX_PAGE:
                try:
                    next_page = driver.find_element(By.XPATH, '//a[text()="下一页"]')
                    driver.execute_script("window.scrollTo(500, document.body.scrollHeight-500);")
                    #next_page.click()
                    print(next_page.get_attribute('href'))
                    if openUrlWithRetry(driver, next_page.get_attribute('href'), 3) <= 0:
                        next_page = ""
                except NoSuchElementException:
                    next_page = ""
                    print ("No more next page")
            else:
                next_page = ""
            _page += 1
    return searchResult

def searchCrawler(driver, keyword, MAX_PAGE):
    print('Keyword is %s, %d page(s)' % (keyword, MAX_PAGE))
    _page = 1
    next_page = "http://s.weibo.com/weibo/" + quote(quote(keyword))

    searchResult = []
    if openUrlWithRetry(driver, next_page, 3) <= 0:
        return searchResult
    while next_page:
        time.sleep(randint(5,15))
        # element = WebDriverWait(driver, 30).until(
        #     EC.presence_of_element_located((By.XPATH, "//div[@id='pl_user_feedList']"))
        #     )
        #driver.execute_script("window.scrollTo(500, document.body.scrollHeight-500);")
        driver.execute_script("window.scrollTo(500, 1000);")

        # star list
        try:
            personList = driver.find_elements_by_xpath('//div[@class="list_star clearfix"]/div[@class="star_detail"]/p[@class="star_name"]/a[@class="name_txt"]')
        except NoSuchElementException:
            print("NoSuchElementException")
            return searchResult
        for person in personList:
            personInfo = []
            try:
                title = person.text
                link = person.get_attribute('href').split('?')[0]
                print(title + ": " + link)
                personInfo.append(title)
                personInfo.append(link)
            except:
                continue
            searchResult.append(personInfo)
            #writer.writerow(searchResult)
            print("---- %d ----" % len(searchResult))

        # feed list
        try:
            personList = driver.find_elements_by_xpath('//div[@action-type="feed_list_item"]//div[contains(@class, "feed_content")]/a[1]')
        except NoSuchElementException:
            print("NoSuchElementException")
            return searchResult
        for person in personList:
            personInfo = []
            try:
                title = person.text
                link = person.get_attribute('href').split('?')[0]
                print(title + ": " + link)
                personInfo.append(title)
                personInfo.append(link)
            except:
                continue
            searchResult.append(personInfo)
            #writer.writerow(searchResult)
            print("---- %d ----" % len(searchResult))


        if _page < MAX_PAGE:
            try:
                next_page = driver.find_element(By.XPATH, '//a[text()="下一页"]')
                driver.execute_script("window.scrollTo(500, document.body.scrollHeight-500);")
                #next_page.click()
                print(next_page.get_attribute('href'))
                if openUrlWithRetry(driver, next_page.get_attribute('href'), 3) <= 0:
                    next_page = ""
            except NoSuchElementException:
                next_page = ""
                print ("No more next page")
        else:
            next_page = ""
        _page += 1
    return searchResult

def createMysqlDB():
    mysqlDB = mysql.connector.connect(host="127.0.0.1",    # your host, usually localhost
                         user="root",         # your username
                         passwd="",  # your password
                         db="influencer")        # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    return mysqlDB

def countMysqlDB(sql):
    mysqlDB = createMysqlDB()
    cur = mysqlDB.cursor()
    try:
        cur.execute(sql)
        count = len(cur.fetchall())
        #print("countMysqlDB: %d" % count)
    except:
        count = 0
    mysqlDB.close()
    return count

def updateMysqlDB(sql):
    mysqlDB = createMysqlDB()
    dbCursor = mysqlDB.cursor()
    try:
        dbCursor.execute(sql)
        mysqlDB.commit()
    except:
        mysqlDB.rollback()
    mysqlDB.close()

def personCrawler(driver, url):
    #listAction = ['//a[text()="文章"]', '//a[text()="全部"]', '//a[text()="原创"]']
    listAction = ['//a[text()="全部"]', '//a[text()="原创"]']
    fans = ''
    description = ''
    avgForward = [0, 0]
    avgComment = [0, 0]
    resForward = ['', '']
    resComment = ['', '']
    forward = [[], []]
    comment = [[], []]
    lastPostTime = [DEFAULT_DATE, DEFAULT_DATE]
    postType = [0, 0, 0, 0]     # 'others', 'picture', 'video', 'article'
    listArticleRead = []
    resArticleRead = ''

    if openUrlWithRetry(driver, url, 5) > 0:
        print(url)
    else:
        return fans, description, avgForward, avgComment, resForward, resComment, lastPostTime, postType, resArticleRead

    for page in range(2):

        time.sleep(randint(5,15))

        if page == 0:
            try:
                fans = driver.find_element_by_xpath('//table[@class="tb_counter"]//span[text()="粉丝"]').find_element_by_xpath('../strong').text
                print(fans + "粉丝")
            except Exception as ex:
                print(ex)
            try:
                description = driver.find_element_by_xpath('//div[@class="PCD_person_info"]/div/p[@class="info"]').text
                print(description)
            except Exception as ex:
                print(ex)

        for idx in range(len(listAction)):

            try:
                ele = driver.find_element(By.XPATH, listAction[idx])
                if not ele.is_displayed():
                    try:
                        # driver.execute_script("document.getElementsByClassName('layer_menu_list')[0].style.display='inline-block';")
                        # ele = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, listAction[idx])))

                        driver.find_element_by_xpath('//li[@node-type="tab_other"]/a[1]').click()
                        # driver.find_element_by_xpath('//div[@class="layer_menu_list"]/li[@action-data="profile_ftype=1&is_ori=1"]/a').click()
                    except:
                        print("Failed to show element")
                ele.click()

            except Exception as ex:
                print("Failed to click... %s" % listAction[idx])
                print(ex)
                continue

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight*3/4);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(randint(3,10))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                wait = WebDriverWait(driver, 20)
                wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="W_pages"]')))
            except:
                print("Maybe no next page...")

            try:
                cardList = driver.find_elements_by_xpath('//div[@node-type="feed_list"]/div[@action-type="feed_list_item"]')
            except NoSuchElementException:
                print("NoSuchElementException")

            for card in cardList:
                # check if this is forward post
                try:
                    card.find_element_by_xpath('.//h4[@class="obj_name S_txt2"]')
                    print("This is liked post, skip...")
                    continue
                except:
                    pass
                # get post date
                try:
                    strPostTime = card.find_element_by_xpath('.//a[@node-type="feed_list_item_date"]').get_attribute('title')
                    postTime = datetime.datetime.strptime(strPostTime, '%Y-%m-%d %H:%M')
                    #print("%s == %s" % (strPostTime, postTime))
                except:
                    postTime = DEFAULT_DATE
                    print("Fail to get post time")

                # check the type of post
                if idx == 1:
                    cardType = 0    # 'others'
                    try:
                        mediaBox = card.find_element_by_xpath('.//div[@class="media_box"]')
                    except Exception as ex:
                        print(ex)
                    try:
                        if mediaBox.find_elements_by_xpath('./ul/li[@action-type="fl_pics"]'):
                            cardType = 1    # 'picture'
                    except:
                        pass
                    try:
                        if mediaBox.find_elements_by_xpath('./ul/li[@node-type="fl_h5_video"]'):
                            cardType = 2    # 'video'
                    except:
                        pass
                    try:
                        if mediaBox.find_elements_by_xpath('./div[@action-type="widget_articleLayer"]'):
                            cardType = 3    # 'article'
                            mediaBox.find_element_by_xpath('./div[@action-type="widget_articleLayer"]/div[1]/div').click()

                            # get view number of article
                            #iframe = driver.find_element_by_xpath('//iframe[contains(@name, "articleLayer")]')
                            iframe = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//iframe[contains(@name, "articleLayer")]')))
                            driver.switch_to_frame(iframe)
                            author = driver.find_element_by_xpath('//div[contains(@class, "authorinfo")]/div/span/a').get_attribute('href')
                            print('author: %s' % author)
                            if url == author:
                                read = driver.find_element_by_xpath('//div[contains(@class, "authorinfo")]/div[@class="W_fr"]/span[@class="num"]').text
                                read.replace('万', '0000')
                                read = re.sub("[^0123456789\.]", '', read)
                                listArticleRead.append(int(read))
                                print('read: %s' % read)
                            driver.find_element_by_xpath('//div[@node-type="sidebar"]/a[1]').click()
                            driver.switch_to_default_content()
                    except Exception as ex:
                        print(ex)
                    postType[cardType] += 1
                    print('type: %d' % cardType)


                # get forward number
                try:
                    forwardNum = card.find_element_by_xpath('.//span[@node-type="forward_btn_text"]//em[2]').text
                    print(forwardNum)
                    forward[idx].append(int(forwardNum))
                except:
                    pass
                # get comment number
                try:
                    commentNum = card.find_element_by_xpath('.//span[@node-type="comment_btn_text"]//em[2]').text
                    print(commentNum)
                    comment[idx].append(int(commentNum))
                except:
                    pass
                if postTime > lastPostTime[idx]:
                    lastPostTime[idx] = postTime
                else:
                    print("%s > %s" % (lastPostTime[idx], postTime))

        try:
            next_page = driver.find_element(By.XPATH, '//a[text()="下一页"]')
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #next_page.click()
            print(next_page.get_attribute('href'))
            if openUrlWithRetry(driver, next_page.get_attribute('href'), 3) <= 0:
                print ("Get next page failed")
                break
        except NoSuchElementException:
            print ("No more next page")
            break


    for idx in range(len(listAction)):
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

    return fans, description, avgForward, avgComment, resForward, resComment, lastPostTime, postType, resArticleRead

def openUrlWithRetry(driver, url, retry):
    countRetry = retry
    while True:
        try:
            driver.get(url)
        except: #TimeoutException:
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

def searchFile(driver, filename, MAX_PAGE):
    try:
        f = open(filename, 'r', newline='', encoding='utf-8')
        reader = csv.reader(f)
    except:
        print("ERROR: file (%s) can't be opened, pleace check again", filename)
        return

    searchResult = []
    for item in reader:
        product_seg = item[0].strip()
        circle = item[1].strip()
        keyword = item[2].strip()
        searchKeyword(driver, product_seg, circle, keyword, MAX_PAGE)

def searchKeyword(driver, product_seg, circle, keyword, MAX_PAGE):
    outfile = product_seg + "_" + circle + "_" + keyword + "_" + str(datetime.date.today()) + '.csv'
    isExist = os.path.exists(outfile)
    fout = open(outfile, 'a', newline='', encoding='utf-8')
    writer = csv.writer(fout)
    if not isExist:
        fout.write('\ufeff')
        writer.writerow(["產品", "圈", "關鍵字", "微博名", "粉絲數", "全部轉發量（全range,均數）", "全部評論數（全range,均數）", "全部最後更新時間", "原創轉發量（全range,均數）",\
         "原創評論數（全range,均數）", "原創最後更新時間", "圖-影-文-其他", "微博上的自我介紹", "鏈結", "官方", "原創文章閱讀量（全range,均數)"])
    personList = searchUserCrawler(driver, keyword, MAX_PAGE)
    personList2 = searchCrawler(driver, keyword, MAX_PAGE)
    # remove duplicate person
    for p2 in personList2:
        for p1 in personList:
            if p2[1] == p1[1]:
                personList2.remove(p2)
                break
    # merge lists
    personList = personList + personList2
    # for p2 in personList2:
    #     p221 = []
    #     p221.append(p2[0])
    #     p221.append(p2[1])
    #     personList.append(p221)


    for person in personList:
        thePerson = person[:]
        fans, description, avgForward, avgComment, resForward, resComment, lastPostTime, postType, resArticleRead = personCrawler(driver, thePerson[1])
        if int(fans) < 10000:
            continue
        thePerson.insert(0, product_seg)
        thePerson.insert(1, circle)
        thePerson.insert(2, keyword)
        thePerson.insert(4, fans)
        thePerson.insert(5, ("%s, %d" % (resForward[0], avgForward[0])))
        thePerson.insert(6, ("%s, %d" % (resComment[0], avgComment[0])))
        thePerson.insert(7, ("%s" % lastPostTime[0]))
        thePerson.insert(8, ("%s, %d" % (resForward[1], avgForward[1])))
        thePerson.insert(9, ("%s, %d" % (resComment[1], avgComment[1])))
        thePerson.insert(10, ("%s" % lastPostTime[1]))
        thePerson.insert(11, ("%d-%d-%d-%d" % (postType[1], postType[2], postType[3], postType[0])))
        thePerson.insert(12, description)
        thePerson.append("V" if "官方" in thePerson[12] else "")
        thePerson.append(resArticleRead)

        sql = "SELECT * FROM Weibo WHERE product_seg='%s' AND circle='%s' AND influencer='%s' AND link='%s'" % (thePerson[0], thePerson[1], thePerson[3], thePerson[13])
        print(sql)
        count = countMysqlDB(sql)
        if count > 0:
            print("Already in database: %d" % count)
        else:
            writer.writerow(thePerson)

        field2Insert = ''
        value2Insert = ''
        if not (resForward[0] == '' and resComment[0] == '' and resForward[1] == '' and resComment[1] == ''):
            field2Insert += "share_avg, comment_avg, share_range, comment_range, ori_share_avg, ori_comment_avg, ori_share_range, ori_comment_range, "
            value2Insert += str(avgForward[0]) + "', '" + str(avgComment[0]) + "', '" + resForward[0] + "', '" + resComment[0] + "', '" \
                + str(avgForward[1]) + "', '" + str(avgComment[1]) + "', '" + resForward[1] + "', '" + resComment[1] + "', '"
        if lastPostTime[0] != DEFAULT_DATE:
            field2Insert += "lastPostTime, "
            value2Insert += str(lastPostTime[0]) + "', '"
        if lastPostTime[1] != DEFAULT_DATE:
            field2Insert += "ori_lastPostTime, "
            value2Insert += str(lastPostTime[1]) + "', '"
        sql = "INSERT INTO Weibo (product_seg, circle, keyword, influencer, follower, " + field2Insert + "post_type, description, link, article_read)" \
            + "VALUES ('" + thePerson[0] + "', '" + thePerson[1] + "', '" + thePerson[2] + "', '" + thePerson[3] + "', '" + fans + "', '" \
            + value2Insert + thePerson[11] + "', '" + thePerson[12] + "', '" + thePerson[13] + "', '" + resArticleRead + "')"
        print(sql)
        updateMysqlDB(sql)
        fout.flush()

    fout.close()

def main(argv):
    MAX_PAGE = 11
    filename = ''
    keyword = ''
    url = ''
    try:
        opts, args = getopt.getopt(argv,"hf:k:u:p:",["filename=", "keyword=", "url=", "page="])
    except getopt.GetoptError:
        print ('weibo_search.py -f <filename> -k <keyword> -u <url> -p <max page>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('weibo_search.py -f <filename> -k <keyword> -u <url> -p <max page>')
            sys.exit()
        elif opt in ('-f', '--filename'):
            filename = arg
            # keyword = arg
            # keyword = keyword.replace('+', ' ')
        elif opt in ('-p', '--maxpage'):
            MAX_PAGE = int(arg)
        elif opt in ('-k', '--keyword'):
            keyword = keyword.replace('+', ' ')
            keyword = arg
        elif opt in ('-u', '--url'):
            url = arg

    #driver = createBrowserChrome()
    driver = createBrowserFirefox()

    if filename != '':
        searchFile(driver, filename, MAX_PAGE)
    elif keyword != '':
        searchKeyword(driver, '', '', keyword, MAX_PAGE)
    elif url != '':
        personCrawler(driver, url)

    driver.quit()
    #display.stop()


if __name__ == "__main__":
   main(sys.argv[1:])
