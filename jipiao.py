#!/usr/bin/env pytho
# -*- coding:utf-8 -*-
'''获取机票价格'''
import threading
import time
from selenium import webdriver
import pymysql
from bs4 import BeautifulSoup
import random

COON = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='120203',
    db='flight',
    charset='utf8')

# 火狐
# driver = webdriver.Firefox()

# PhantomJS
driver = webdriver.PhantomJS('phantomjs.exe')


def get_message(dep_city_name, dep_city, dep_date, arr_city_name, arr_city,
                arr_date):
    '''开启浏览器'''
    now_url = driver.current_url
    if now_url == 'about:blank':
        url = "https://sjipiao.alitrip.com/flight_search_result.htm?_input_charset=utf-8&spm=181.7091613.a1z67.1001&searchBy=1280&tripType=0&depCityName=" + dep_city_name + "&depCity=" + dep_city + "&depDate=" + dep_date + "&arrCityName=" + arr_city_name + "&arrCity=" + arr_city + "&arrDate=" + arr_date
        driver.get(url)
    else:
        re_search = driver.find_elements_by_css_selector("input[value='搜索航班']")
        re_search[0].click()
    return get_messahe(dep_date)


def get_messahe(dep_date):
    '''获取页面信息'''
    # 将焦点锁定在新的弹出框上
    driver.current_window_handle
    close_table = driver.find_elements_by_css_selector(
        "a[id^=ks-overlay-close-ks-component]")
    alert_table = driver.find_elements_by_css_selector("div[id^=ks-component]")
    re_search = driver.find_elements_by_css_selector("input[value='搜索航班']")
    if len(alert_table) == 1:
        # 切入iframe
        driver.switch_to_frame(0)
        print u'登陆飞猪'
        driver.find_element_by_id("TPL_username_1").send_keys("13651742164")
        driver.find_element_by_id("TPL_password_1").send_keys("120203wang!")
        driver.find_element_by_id("J_SubmitStatic").submit()
        driver.switch_to_default_content()
        close_table[0].click()
        re_search[0].click()
    driver.switch_to_default_content()
    bs_obj = BeautifulSoup(driver.page_source, "html.parser")
    msg_before_list = bs_obj.findAll("tr", {"class": "flight-item-tr"})
    msg_list = []
    for bean in msg_before_list:
        # yapf:disable
        tup = (
            bean.find("span", {"class": "J_line J_TestFlight"}).string,
            dep_date,
            bean.find("p", {"class": "flight-time-deptime"}).string,
            bean.find("span", {"class": "s-time"}).string,
            bean.find('p', {'class': 'port-dep'}).string,
            bean.find('p', {'class': 'port-arr'}).string,
            bean.select("td[class='flight-ontime-rate']")[0].find('p').text,
            bean.find("span", {"class": "J_FlightListPrice"}).string,
            bean.find("span", {"class": "discount"}).string
        )
        # yapf:enable
        msg_list.append(tup)
    return msg_list


def save_message(save_list):
    '''保存数据'''
    # 创建游标
    cursor = COON.cursor()
    try:
        sql = "insert into flight_ticket(flight_num,fly_date,dep_time,arr_time,dep_airport,arr_airport,ontime_rate,flight_price,discount) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        # 执行SQL，并返回受影响行数,执行多次
        weffect_row = cursor.executemany(sql, save_list)
        print weffect_row
        # 提交，不然无法保存新建或者修改的数据
        COON.commit()
    except Exception, e:
        print e
    finally:
        # 关闭游标
        cursor.close()


def get_ticket(dep_airport,dep_airport_code,arr_airport,arr_airport_code,fly_date):
    '''主程序'''
    print u'主程序执行:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    ticketlist = get_message(dep_airport, dep_airport_code, fly_date, arr_airport,arr_airport_code, '')
    save_message(ticketlist)
    print threading.current_thread()
    print threading.enumerate()

count = 1

def hello():
    '''定时'''
    global count
    print count
    print u'定时器程序执行:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    count += 1
    parameterList = get_parameter()
    for parameter in parameterList:
        interval = random.randint(0, 600)
        print u'延迟:',interval
        timer = threading.Timer(interval,get_ticket,(parameter[1], parameter[2], parameter[3], parameter[4], parameter[5]))
        timer.start()
    timer = threading.Timer(600.0, hello)
    timer.start()
    if count > 100:
        # 关闭链接
        COON.close()
        timer.cancel()


def get_parameter():
    # 创建游标
    cursor = COON.cursor()
    try:
        sql = "select * from flight_parameter where status = 0"
        # 执行SQL，并返回受影响行数,执行多次
        cursor.execute(sql)
        infoList = cursor.fetchall()
        return infoList
    except Exception as e:
        print e
    finally:
        # 关闭游标
        cursor.close()

hello()
