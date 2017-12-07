# -- coding: utf-8 -- –
import os, sys, getopt
import csv
import mysql.connector
import datetime
from weibo_common import queryAllMysqlDB

def main(argv):
    maxId = 0
    idx = 0
    try:
        opts, args = getopt.getopt(argv,"he:",["filename="])
    except getopt.GetoptError:
        print ('weibo_keyword.py -f <csv filename>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('weibo_keyword.py -e id')
            sys.exit()
        elif opt in ('-e', '--export'):
            idx = arg

    sql = 'SELECT k.product_seg, k.circle, k.keyword, r.influencer, r.follower, r.share_avg, r.comment_avg, r.share_range, r.comment_range, r.lastPostTime, \
            r.ori_share_avg, r.ori_comment_avg, r.ori_share_range, r.ori_comment_range, r.ori_lastPostTime, \
            r.key_share_avg, r.key_comment_avg, r.key_share_range, r.key_comment_range, \
            r.post_type, r.description, r.link, r.article_read, r.key_content, r.official, r.id \
        FROM Weibo AS r, Weibo_keyword AS k \
        WHERE r.id > "{}" AND r.post_type != "" AND k.id = r.keyword_id AND r.lastPostTime > DATE_SUB(CURDATE(), INTERVAL 6 MONTH) \
        ORDER BY k.circle, k.keyword, r.key_content DESC, r.follower DESC'.format(idx)
    accountList = queryAllMysqlDB(sql)

    for account in accountList:
        if int(account[25]) > maxId:
            maxId = int(account[25])
        product_seg = account[0]
        circle = account[1]
        keyword = account[2]
        influencer = account[3]
        fans = account[4]
        resShare = '{}, {}'.format(account[7], account[5])
        resComment = '{}, {}'.format(account[8], account[6])
        lastPostTime = account[9]
        resShareOri = '{}, {}'.format(account[12], account[10])
        resCommentOri = '{}, {}'.format(account[13], account[11])
        lastPostTimeOri = account[14]
        resShareKey = '{}, {}'.format(account[17], account[15])
        resCommentKey = '{}, {}'.format(account[18], account[16])
        postType = account[19]
        info = account[20]
        link = account[21]
        articleRead = account[22]
        keyContent = account[23]
        official = "V" if account[24] else ""

        outfile = product_seg + "_" + circle + "_" + keyword + "_" + str(datetime.date.today()) + '.csv'
        isExist = os.path.exists(outfile)
        with open(outfile, 'a', newline='', encoding='utf-8') as fout:
            writer = csv.writer(fout)
            if not isExist:
                fout.write('\ufeff')
                writer.writerow(["產品", "圈", "關鍵字", "微博名", "粉絲數", "全部轉發量（全range,均數）", "全部評論數（全range,均數）", "全部最後更新時間", \
                "原創轉發量（全range,均數）", "原創評論數（全range,均數）", "原創最後更新時間", "原創有關鍵字轉發量（全range,均數）", "原創有關鍵字評論數（全range,均數）", \
                "原創文章閱讀量（全range,均數)", "原創貼文相關性", "圖-影-文-其他", "官方/有限公司", "微博上的自我介紹", "鏈結"])
            row = [product_seg, circle, keyword, influencer, fans, resShare, resComment, lastPostTime, \
                resShareOri, resCommentOri, lastPostTimeOri, resShareKey, resCommentKey, \
                articleRead, keyContent, postType, official, info, link]

            writer.writerow(row)

    print("LAST ID: {}".format(maxId))
    open(str(maxId), 'a', newline='', encoding='utf-8').close()

if __name__ == "__main__":
   main(sys.argv[1:])
