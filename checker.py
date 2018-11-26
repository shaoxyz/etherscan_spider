# -*- coding:utf-8 -*-
# Python3
# File    : checker
# Time    : 2018/7/9 10:32
# Author  : Shaweb

# ---------------------
import requests
from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

import time


def send_email(SMTP_host="smtp.163.com",
               nick_name="按时汇报的可乐",  # 邮件昵称
               from_account="shwb95@163.com",
               from_passwd="shaowanbo110",
               to_account="584927688@qq.com",
               title="Niuco_Service",
               content=""):
    # initial
    email_client = SMTP_SSL(SMTP_host)
    email_client.login(from_account, from_passwd)
    # create msg
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    HTML = "{}<p>----小纽扣于{}如是向主人汇报</p>".format(content, now)

    msg = MIMEText(HTML, _subtype='html', _charset='utf-8')
    msg['Subject'] = Header(title, 'utf-8')  # subject
    msg['From'] = nick_name
    msg['To'] = to_account
    email_client.sendmail(from_account, to_account, msg.as_string())

    email_client.quit()


def check_services(services):
    for s in services:
        try:
            now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            r = requests.get(services[s], timeout=10)
            print(s, 'pass at {}'.format(now))
        except:
            return s

    return True


if __name__ == '__main__':
    urls = {"spider": "http://115.159.28.31:3001/gasPrice",
            "node": "http://115.159.28.31:3000/utils/getCost"}
    while True:
        b = check_services(urls)
        if not b:
            send_email(content="{}服务挂了！".format(b))
        time.sleep(600)
