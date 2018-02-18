# -*-coding:utf-8-*-
__author__ = 'hf'

import xlwt
import sys
import os
import pandas as pd
import datetime
import time  # 时间相关操作
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from collections import Counter
import requests as rst
import pickle
# import urllib3.request as rst
import Odatas as sd

#reload(sys)
#sys.setdefaultencoding('utf-8')

# ROWCT = 1
TEST = False
WORKBOOK = "./basedata/train1.xls"
TEMPBOOK = "./basedata/temp.xls"
SHEET = "game_data"
DUMPSIZE = 10

def tprint(*args, sep=' ', end='\n', file=sys.stdout, flush=False):
    if TEST:
        print(args, sep=' ', end='\n', file=sys.stdout, flush=False)
    return

def getworkbook(wbname = WORKBOOK, sheetname = SHEET):
    wb = xlwt.Workbook(encoding='utf-8')
    st = wb.add_sheet(sheetname, cell_overwrite_ok=True)
    # print(wb, st)
    return wb, st

def writecolumns(workbook, sheet, cols=sd.COLUMNNAME):
    print("write the columns:")
    for i in range(0, len(cols)):
        sheet.write(0, i, cols[i])
    workbook.save(TEMPBOOK)

def writexls(workbook, sheet, cols=sd.COLUMNNAME, data=None):
    for i in range(len(data)):
        print("write the data:%s"%i )
        eachrow = data[i]
        for j in range(len(eachrow)):
            sheet.write(i+1, j, eachrow[cols[j]])
    workbook.save(TEMPBOOK)

def appendxls(workbook, sheet, cols=sd.COLUMNNAME, rowcount=0,data=None):
    print("write the data:%s" %rowcount)
    for j in range(len(data)):
        sheet.write(rowcount, j, data[cols[j]])
    workbook.save(TEMPBOOK)

# 获取网页中的基本的信息代码：
def get_js_basic(url, idd):
    final = {}
    browser = webdriver.PhantomJS()
    browser.get(url)
    # tprint(browser.page_source)
    try:
        final['id'] = idd
        # host = broswer.find_elements_by_id('link126').text
        # guest = broswer.find_elements_by_id('link135').text
        #获取当前比赛的联赛信息
        print("get the team rank of %s" %idd)
        teamsrank = get_team_info(browser)
        ##############################################################################################################
        # 基础信息
        print("get the basic game info of %s" % idd)
        game_basic_info(browser, final)
        ##############################################################################################################
        #胜负进球信息
        print("get the shengfu info of %s" % idd)
        game_shengfu(browser, final)
        ##############################################################################################################
        #交战历史
        print("get the jiaozhan info of %s" % idd)
        jiaozhan_history(browser, final)
        #相同赛事的交战历史
        print("get the jiaozhan info of same game of %s" % idd)
        jiaozhan_history_xiangtongsaishi(browser, final)
        ######################################################################################################
        #近期赛事--主队信息
        print("get the host info of %s" % idd)
        rencent_gameinfo_host(browser, final)
        #近期赛事--主队在主场
        print("get the host info as host of %s" % idd)
        rencent_gameinfo_hostashost(browser, final)

        ######################################################################################################
        #近期赛事--客场信息
        print("get the guest info of %s" % idd)
        rencent_gameinfo_guest(browser, final)
        #近期赛事--客队在客场
        print("get the guest info as guest of %s" % idd)
        rencent_gameinfo_guestasguest(browser, final)
        ######################################################################################################
        #未来赛事
        print("get the future game info of %s" % idd)
        future_game(browser, final, teamsrank)

        # print future_guest
        print(final)
        browser.quit()
        return final
    except:
        browser.quit()
        print("error in getting the information of %s" % idd)
        return None


def future_game(browser, final, teamsrank):
    # 未来赛事
    if not teamsrank:
        final["future_guest_score"] = ""
        final["future_host_score"] = ""
        return
    future_host_rank = []
    future_host_days = []
    hostscores = 0
    i = 1
    while True:
        i+=1
        xpath1 = "//div[@class='odds_content']/div[@class='M_box integral'][1]/div/div[1]/table/tbody/tr[%s]/td[3]"%i
        # xpath2 = "//div[@class='odds_content']/div[@class='M_box integral'][1]/div/div[1]/table/tbody/tr[%s]/td[4]" % i

        try:
            futuregameinfo1 = browser.find_element_by_xpath(xpath1).text
            tprint(futuregameinfo1)
            # futuregameinfo2 = browser.find_element_by_xpath(xpath2).text
            # tprint(futuregameinfo2)
            if futuregameinfo1:
                first = futuregameinfo1[:futuregameinfo1.find("\n")]
                sec = futuregameinfo1[futuregameinfo1.rfind("\n")+1:]
                if first == final["host_name"]:
                    future_host_rank.append(teamsrank[sec])
                elif sec == final["host_name"]:
                    future_host_rank.append(teamsrank[first])
                else:
                    future_host_rank.append(0)
            else:
                break
            # if futuregameinfo2:
            #     future_host_days.append(int(futuregameinfo2[:futuregameinfo2.find("天")]))
            # lenfg = min(len(futuregameinfo1), len(futuregameinfo2))
        except:
            tprint("cannot find more items from future_games")
            break
    for each in future_host_rank:
        hostscores += each
    tprint(hostscores)
    final["future_host_score"] = hostscores

    future_guest_rank = []
    future_guest_days = []
    guestscores = 0
    i = 1
    while True:
        i += 1
        xpath1 = "//div[@class='odds_content']/div[@class='M_box integral'][1]/div/div[2]/table/tbody/tr[%s]/td[3]" % i
        # xpath2 = "//div[@class='odds_content']/div[@class='M_box integral'][1]/div/div[1]/table/tbody/tr[%s]/td[4]" % i

        try:
            futuregameinfo1 = browser.find_element_by_xpath(xpath1).text
            tprint(futuregameinfo1)
            # futuregameinfo2 = browser.find_element_by_xpath(xpath2).text
            # tprint(futuregameinfo2)
            if futuregameinfo1:
                first = futuregameinfo1[:futuregameinfo1.find("\n")]
                sec = futuregameinfo1[futuregameinfo1.rfind("\n") + 1:]
                if first == final["guest_name"]:
                    future_guest_rank.append(teamsrank[sec])
                elif sec == final["guest_name"]:
                    future_guest_rank.append(teamsrank[first])
                else:
                    future_guest_rank.append(0)
            else:
                break
                # if futuregameinfo2:
                #     future_guest_days.append(int(futuregameinfo2[:futuregameinfo2.find("天")]))
                # lenfg = min(len(futuregameinfo1), len(futuregameinfo2))
        except:
            tprint("cannot find more items from future_games")
            break
    tprint(future_guest_rank)
    for each in future_guest_rank:
        guestscores += each

    tprint(guestscores)
    final["future_guest_score"] = guestscores
    #
    #     for td in tds:
    #         s = td.text
    #         tprint(s)
    #         if s.find('天') == -1:
    #             pass
    #         else:
    #             future_host.append(s[:-1])
    # final['future_host1'] = future_host[0]
    # final['future_host2'] = future_host[1]
    # final['future_host3'] = future_host[2]
    # future_guest = []
    # for i in range(1, 5):
    #     xpath = "//div[@class='M_box integral'][1]/div[@class='M_content']/div[@class='team_b']/table/tbody/tr[%s]" % str(
    #         i)
    #     tr = browser.find_element_by_xpath(xpath)
    #     # print tr.text
    #     tds = tr.find_elements_by_tag_name('td')
    #     for td in tds:
    #         s = td.text
    #         if s.find('天') == -1:
    #             pass
    #         else:
    #             future_guest.append(s[:-1])
    # final['future_guest1'] = future_guest[0]
    # final['future_guest2'] = future_guest[1]
    # final['future_guest3'] = future_guest[2]


def rencent_gameinfo_guestasguest(browser, final):
    guestname = []
    for i in range(3, 13):
        xpath = "//div[@id='team_zhanji2_0']/form[@id='zhanji_20']/div[@class='M_content']/table/tbody/tr[%s]/td[3]" % i
        each = browser.find_element_by_xpath(xpath).text
        eachhost = each[:each.find('\n')]
        eachguest = each[each.rfind('\n')+1:]
        guestname.append(eachguest)
    c = Counter(guestname)
    c = sorted(c, key=lambda a: a[1], reverse=True)
    final['guest_name'] = c[0]
    tprint("guest_name", guestname)

    xpath = "//div[@id='team_zhanji2_0']/form[@id='zhanji_20']/div[3]/div/p"
    zhanji = browser.find_element_by_xpath(xpath).text
    # print zhanji
    jin = zhanji.find('近')
    chang = zhanji.find('场')
    ji = zhanji.find('绩')
    sheng = zhanji.find('胜')
    ping = zhanji.find('平')
    fu = zhanji.find('负')
    jin2 = zhanji.find('进')
    qiu1 = zhanji.find('球')
    shi = zhanji.find('失')
    qiu2 = zhanji.find('球', shi + 1)
    total_guest2 = zhanji[jin + 1:chang]
    sheng_guest2 = zhanji[ji + 1:sheng]
    ping_guest2 = zhanji[sheng + 1:ping]
    fu_guest2 = zhanji[ping + 1:fu]
    jin_guest2 = zhanji[jin2 + 1:qiu1]
    shi_guest2 = zhanji[shi + 1:qiu2]
    # print total_guest2, sheng_guest2, ping_guest2, fu_guest2, jin_guest2, shi_guest2
    final['recent_guestasguest_total'] = total_guest2
    final['recent_guestasguest_sheng'] = sheng_guest2
    final['recent_guestasguest_ping'] = ping_guest2
    final['recent_guestasguest_fu'] = fu_guest2
    final['recent_guestasguest_shenglv'] = 1.0 * float(sheng_guest2) / float(total_guest2)
    final['recent_guestasguest_pinglv'] = 1.0 * float(ping_guest2) / float(total_guest2)
    final['recent_guestasguest_fulv'] = 1.0 * float(fu_guest2) / float(total_guest2)
    final['recent_guestasguest_jinqiu'] = jin_guest2
    final['recent_guestasguest_shiqiu'] = shi_guest2
    final['recent_guestasguest_jingqiu'] = 1.0 * float(jin_guest2) - float(shi_guest2)
    final['recent_guestasguest_jinqiulv'] = 1.0 * float(jin_guest2) / float(total_guest2)
    final['recent_guestasguest_shiqiulv'] = 1.0 * float(shi_guest2) / float(total_guest2)
    final['recent_guestasguest_jingqiulv'] = 1.0 * (float(jin_guest2) - float(shi_guest2)) / float(total_guest2)


def rencent_gameinfo_guest(browser, final):
    xpath = "//div[@id='team_zhanji_0']/form[@id='zhanji_00']/div[3]/div/p"
    zhanji = browser.find_element_by_xpath(xpath).text
    # print zhanji
    jin = zhanji.find('近')
    chang = zhanji.find('场')
    ji = zhanji.find('绩')
    sheng = zhanji.find('胜')
    ping = zhanji.find('平')
    fu = zhanji.find('负')
    jin2 = zhanji.find('进')
    qiu1 = zhanji.find('球')
    shi = zhanji.find('失')
    qiu2 = zhanji.find('球', shi + 1)
    total_guest = zhanji[jin + 1:chang]
    sheng_guest = zhanji[ji + 1:sheng]
    ping_guest = zhanji[sheng + 1:ping]
    fu_guest = zhanji[ping + 1:fu]
    jin_guest = zhanji[jin2 + 1:qiu1]
    shi_guest = zhanji[shi + 1:qiu2]
    # print total_guest, sheng_guest, ping_guest, fu_guest, jin_guest, shi_guest
    final['recent_guest_total'] = total_guest
    final['recent_guest_sheng'] = sheng_guest
    final['recent_guest_ping'] = ping_guest
    final['recent_guest_fu'] = fu_guest
    final['recent_guest_shenglv'] = 1.0 * float(sheng_guest) / float(total_guest)
    final['recent_guest_pinglv'] = 1.0 * float(ping_guest) / float(total_guest)
    final['recent_guest_fulv'] = 1.0 * float(fu_guest) / float(total_guest)
    final['recent_guest_jinqiu'] = jin_guest
    final['recent_guest_shiqiu'] = shi_guest
    final['recent_guest_jingqiu'] = 1.0 * float(jin_guest) - 1.0 * float(shi_guest)
    final['recent_guest_jinqiulv'] = 1.0 * float(jin_guest) / float(total_guest)
    final['recent_guest_shiqiulv'] = 1.0 * float(shi_guest) / float(total_guest)
    final['recent_guest_jingqiulv'] = 1.0 * (float(jin_guest) - float(shi_guest)) / float(total_guest)


def rencent_gameinfo_hostashost(browser, final):
    #get the host short name
    hostname = []
    for i in range(3, 13):
        xpath = "//div[@id='team_zhanji2_1']/form[@id='zhanji_11']/div/table/tbody/tr[%s]/td[3]"%i
        each = browser.find_element_by_xpath(xpath).text
        eachhost = each[:each.find('\n')]
        eachguest = each[each.rfind('\n'):]
        hostname.append(eachhost)
    c = Counter(hostname) 
    c = sorted(c, key=lambda a:a[1], reverse=True)
    final['host_name'] = c[0]

    tprint("hostname", hostname)
    #get the recent host game information as a host
    xpath = "//div[@id='team_zhanji2_1']/form[@id='zhanji_11']/div[3]/div/p"
    zhanji = browser.find_element_by_xpath(xpath).text
    # print zhanji
    jin = zhanji.find('近')
    chang = zhanji.find('场')
    ji = zhanji.find('绩')
    sheng = zhanji.find('胜')
    ping = zhanji.find('平')
    fu = zhanji.find('负')
    jin2 = zhanji.find('进')
    qiu1 = zhanji.find('球')
    shi = zhanji.find('失')
    qiu2 = zhanji.find('球', shi + 1)
    total_host2 = zhanji[jin + 1:chang]
    sheng_host2 = zhanji[ji + 1:sheng]
    ping_host2 = zhanji[sheng + 1:ping]
    fu_host2 = zhanji[ping + 1:fu]
    jin_host2 = zhanji[jin2 + 1:qiu1]
    shi_host2 = zhanji[shi + 1:qiu2]
    # print total_host2, sheng_host2, ping_host2, fu_host2, jin_host2, shi_host2
    final['recent_hostashost_total'] = total_host2
    final['recent_hostashost_sheng'] = sheng_host2
    final['recent_hostashost_ping'] = ping_host2
    final['recent_hostashost_fu'] = fu_host2
    final['recent_hostashost_shenglv'] = 1.0 * float(sheng_host2) / float(total_host2)
    final['recent_hostashost_pinglv'] = 1.0 * float(ping_host2) / float(total_host2)
    final['recent_hostashost_fulv'] = 1.0 * float(fu_host2) / float(total_host2)
    final['recent_hostashost_jinqiu'] = jin_host2
    final['recent_hostashost_shiqiu'] = shi_host2
    final['recent_hostashost_jingqiu'] = 1.0 * float(jin_host2) - 1.0 * float(shi_host2)
    final['recent_hostashost_jinqiulv'] = 1.0 * float(jin_host2) / float(total_host2)
    final['recent_hostashost_shiqiulv'] = 1.0 * float(shi_host2) / float(total_host2)
    final['recent_hostashost_jingqiulv'] = 1.0 * (float(jin_host2) - float(shi_host2)) / float(total_host2)



def rencent_gameinfo_host(browser, final):
    # print '近期战绩'
    xpath = "//div[@id='team_zhanji_1']/form[@id='zhanji_01']/div[3]/div/p"
    zhanji = browser.find_element_by_xpath(xpath).text
    jin = zhanji.find('近')
    chang = zhanji.find('场')
    ji = zhanji.find('绩')
    sheng = zhanji.find('胜')
    ping = zhanji.find('平')
    fu = zhanji.find('负')
    jin2 = zhanji.find('进')
    qiu1 = zhanji.find('球')
    shi = zhanji.find('失')
    qiu2 = zhanji.find('球', shi + 1)
    total_host = zhanji[jin + 1:chang]
    sheng_host = zhanji[ji + 1:sheng]
    ping_host = zhanji[sheng + 1:ping]
    fu_host = zhanji[ping + 1:fu]
    jin_host = zhanji[jin2 + 1:qiu1]
    shi_host = zhanji[shi + 1:qiu2]
    # print total_host, sheng_host, ping_host, fu_host, jin_host, shi_host
    final['recent_host_total'] = total_host
    final['recent_host_sheng'] = sheng_host
    final['recent_host_ping'] = ping_host
    final['recent_host_fu'] = fu_host
    final['recent_host_shenglv'] = 1.0 * float(sheng_host) / float(total_host)
    final['recent_host_pinglv'] = 1.0 * float(ping_host) / float(total_host)
    final['recent_host_fulv'] = 1.0 * float(fu_host) / float(total_host)
    final['recent_host_jinqiu'] = jin_host
    final['recent_host_shiqiu'] = shi_host
    final['recent_host_jingqiu'] = 1.0 * float(jin_host) - 1.0 * float(shi_host)
    final['recent_host_jinqiulv'] = 1.0 * float(jin_host) / float(total_host)
    final['recent_host_shiqiulv'] = 1.0 * float(shi_host) / float(total_host)
    final['recent_host_jingqiulv'] = 1.0 * (float(jin_host) - float(shi_host)) / float(total_host)


def jiaozhan_history_xiangtongsaishi(browser, final):
    try:
        # browser.get(url)
        # print '相同赛事'
        xpath = "//div[@id='team_jiaozhan']/div[@class='M_content_t']/form/div/div[1]"
        alll = browser.find_element_by_xpath(xpath)
        ActionChains(browser).move_to_element(alll).perform()
        xpath1 = "//div[@id='team_jiaozhan']/div[@class='M_content_t']/form/div/div[1]/ul/li[2]"
        same1 = browser.find_element_by_xpath(xpath1)
        # print same1.text
        same1.click()
        time.sleep(0.5)
        xpath = "//div[@id='team_jiaozhan']/div[@class='M_title']/span/span[1]"
        recent_jiaozhan_same = browser.find_element_by_xpath(xpath).text
        # print recent_jiaozhan_same
        final['recent_jiaozhan_total_same'] = recent_jiaozhan_same
        xpath = "//div[@id='team_jiaozhan']/div[@class='M_title']/span/span[2]/em"
        recent_result = browser.find_elements_by_xpath(xpath)
        recent_results = []
        for re in recent_result:
            recent_results.append(re.text[:-1])
        # print recent_results
        final['recent_same_sheng'] = recent_results[0]
        final['recent_same_ping'] = recent_results[1]
        final['recent_same_fu'] = recent_results[2]
        final['recent_same_shenglv'] = 1.0 * float(recent_results[0]) / float(recent_jiaozhan_same)
        final['recent_same_pinglv'] = 1.0 * float(recent_results[1]) / float(recent_jiaozhan_same)
        final['recent_same_fulv'] = 1.0 * float(recent_results[2]) / float(recent_jiaozhan_same)
        xpath = "//div[@id='team_jiaozhan']/div[@class='M_title']/span"
        qius = browser.find_element_by_xpath(xpath).text
        jin = qius.find('进')
        qiu = qius.find('球')
        jinqiu = qius[jin + 1:qiu]
        shi = qius.find('失')
        qiu = qius.find('球', qiu + 1)
        shiqiu = qius[shi + 1:qiu]
        qiu = qius.find('球', qiu + 1)
        ci = qius.find('次', qiu + 1)
        daqiu = qius[qiu + 1:ci]
        qiu = qius.find('球', qiu + 1)
        ci = qius.find('次', ci + 1)
        xiaoqiu = qius[qiu + 1: ci]
        # print '进球', jinqiu, 'shiqiu', shiqiu, 'daqiu', daqiu, 'xiaoqiu', xiaoqiu
        final['jiaozhan_same_jinqiu'] = jinqiu
        final['jiaozhan_same_shiqiu'] = shiqiu
        final['jiaozhan_same_jingqiu'] = 1.0 * float(jinqiu) - 1.0 * float(shiqiu)
        final['jiaozhan_same_jinqiulv'] = 1.0 * float(jinqiu) / float(recent_jiaozhan_same)
        final['jiaozhan_same_shiqiulv'] = 1.0 * float(shiqiu) / float(recent_jiaozhan_same)
        final['jiaozhan_same_jingqiulv'] = 1.0 * (float(jinqiu) - float(shiqiu)) / float(recent_jiaozhan_same)
        final['jiaozhan_same_daqiu'] = daqiu
        final['jiaozhan_same_xiaoqiu'] = xiaoqiu
        xpath = "//div[@id='team_jiaozhan']/div[@class='M_content']/table/tbody/tr"
        trs = browser.find_elements_by_xpath(xpath)
        count = len(trs)
        # print count
    except:
        final['recent_jiaozhan_total_same'] = ''
        final['recent_same_sheng'] = ''
        final['recent_same_ping'] = ''
        final['recent_same_fu'] = ''
        final['recent_same_shenglv'] = ''
        final['recent_same_pinglv'] = ''
        final['recent_same_fulv'] = ''
        final['jiaozhan_same_jinqiu'] = ''
        final['jiaozhan_same_shiqiu'] = ''
        final['jiaozhan_same_jingqiu'] = ''
        final['jiaozhan_same_jinqiulv'] = ''
        final['jiaozhan_same_shiqiulv'] = ''
        final['jiaozhan_same_jingqiulv'] = ''
        final['jiaozhan_same_daqiu'] = ''
        final['jiaozhan_same_xiaoqiu'] = ''


def jiaozhan_history(browser, final):
    # print '交战历史'
    try:
        xpath = "//div[@id='team_jiaozhan']/div[@class='M_title']/span/span[1]"
        recent_jiaozhan_total = browser.find_element_by_xpath(xpath).text
        # print recent_jiaozhan_total
        final['recent_jiaozhan_total'] = recent_jiaozhan_total
        xpath = "//div[@id='team_jiaozhan']/div[@class='M_title']/span/span[2]/em"
        recent_result = browser.find_elements_by_xpath(xpath)
        recent_results = []
        for re in recent_result:
            recent_results.append(re.text[:-1])
        # print recent_results
        final['jiaozhan_sheng'] = recent_results[0]
        final['jiaozhan_ping'] = recent_results[1]
        final['jiaozhan_fu'] = recent_results[2]
        final['jiaozhan_shenglv'] = 1.0 * float(recent_results[0]) / float(recent_jiaozhan_total)
        final['jiaozhan_pinglv'] = 1.0 * float(recent_results[1]) / float(recent_jiaozhan_total)
        final['jiaozhan_fulv'] = 1.0 * float(recent_results[2]) / float(recent_jiaozhan_total)
        xpath = "//div[@id='team_jiaozhan']/div[@class='M_title']/span"
        qius = browser.find_element_by_xpath(xpath).text
        jin = qius.find('进')
        qiu = qius.find('球')
        jinqiu = qius[jin + 1:qiu]
        shi = qius.find('失')
        qiu = qius.find('球', qiu + 1)
        shiqiu = qius[shi + 1:qiu]
        qiu = qius.find('球', qiu + 1)
        ci = qius.find('次', qiu + 1)
        daqiu = qius[qiu + 1:ci]
        qiu = qius.find('球', qiu + 1)
        ci = qius.find('次', ci + 1)
        xiaoqiu = qius[qiu + 1: ci]
        # print '进球', jinqiu, 'shiqiu', shiqiu, 'daqiu', daqiu, 'xiaoqiu', xiaoqiu
        final['jiaozhan_jinqiu'] = jinqiu
        final['jiaozhan_shiqiu'] = shiqiu
        final['jiaozhan_jingqiu'] = 1.0 * float(jinqiu) - 1.0 * float(shiqiu)
        final['jiaozhan_jinqiulv'] = 1.0 * float(jinqiu) / float(recent_jiaozhan_total)
        final['jiaozhan_shiqiulv'] = 1.0 * float(shiqiu) / float(recent_jiaozhan_total)
        final['jiaozhan_jingqiulv'] = 1.0 * (float(jinqiu) - float(shiqiu)) / float(recent_jiaozhan_total)
        final['jiaozhan_daqiu'] = daqiu
        final['jiaozhan_xiaoqiu'] = xiaoqiu
        xpath = "//div[@id='team_jiaozhan']/div[@class='M_content']/table/tbody/tr"
        trs = browser.find_elements_by_xpath(xpath)
        count = len(trs)
    except:
        print('双方无交战历史')
        final['recent_jiaozhan_total'] = ''
        final['jiaozhan_sheng'] = ''
        final['jiaozhan_ping'] = ''
        final['jiaozhan_fu'] = ''
        final['jiaozhan_shenglv'] = ''
        final['jiaozhan_pinglv'] = ''
        final['jiaozhan_fulv'] = ''
        final['jiaozhan_jinqiu'] = ''
        final['jiaozhan_shiqiu'] = ''
        final['jiaozhan_jingqiu'] = ''
        final['jiaozhan_jinqiulv'] = ''
        final['jiaozhan_shiqiulv'] = ''
        final['jiaozhan_jingqiulv'] = ''
        final['jiaozhan_daqiu'] = ''
        final['jiaozhan_xiaoqiu'] = ''


def game_shengfu(browser, final):
    # print '赛前联赛积分排名: '
    # print '场次', '胜', '平', '负', '	进', '失', '净', '积分', '排名', '胜率','平率','负率','进球率','失球率','净胜球率'
    liss = ['count', 'sheng', 'ping', 'fu', 'jinqiu', 'shiqiu', 'jingqiu', 'jifen', 'rank',
            'shenglv', 'pinglv', 'fulv', 'jinqiulv', 'shiqiulv', 'jingqiulv']
    total_a = []
    host_a = []
    guest_a = []
    for i in range(2, 5):
        xpath = "//div[@class='team_a']/table/tbody/tr[%s]" % str(i)
        tr = browser.find_element_by_xpath(xpath)
        if i == 2:
            tds = tr.find_elements_by_tag_name('td')
            for td in tds:
                total_a.append(td.text)
            for j in range(2, 8):
                total_a.append(1.0 * float(total_a[j]) / float(total_a[1]))
        if i == 3:
            tds = tr.find_elements_by_tag_name('td')
            for td in tds:
                host_a.append(td.text)
            for j in range(2, 8):
                host_a.append(1.0 * float(host_a[j]) / float(host_a[1]))
        if i == 4:
            tds = tr.find_elements_by_tag_name('td')
            for td in tds:
                guest_a.append(td.text)
            for j in range(2, 8):
                guest_a.append(1.0 * float(guest_a[j]) / float(guest_a[1]))
    del (total_a[0])
    del (host_a[0])
    del (guest_a[0])
    # print total_a
    # print host_a
    # print guest_a
    total_b = []
    host_b = []
    guest_b = []
    for i in range(2, 5):
        xpath = "//div[@class='team_b']/table/tbody/tr[%s]" % str(i)
        tr = browser.find_element_by_xpath(xpath)
        if i == 2:
            tds = tr.find_elements_by_tag_name('td')
            for td in tds:
                total_b.append(td.text)
            for j in range(2, 8):
                total_b.append(1.0 * float(total_b[j]) / float(total_b[1]))
        if i == 3:
            tds = tr.find_elements_by_tag_name('td')
            for td in tds:
                host_b.append(td.text)
            for j in range(2, 8):
                host_b.append(1.0 * float(host_b[j]) / float(host_b[1]))
        if i == 4:
            tds = tr.find_elements_by_tag_name('td')
            for td in tds:
                guest_b.append(td.text)
            for j in range(2, 8):
                guest_b.append(1.0 * float(guest_b[j]) / float(guest_b[1]))
    del (total_b[0])
    del (host_b[0])
    del (guest_b[0])
    # print '场次', '胜', '平', '负', '	进', '失', '净', '积分', '	排名', '胜率'
    # print total_b
    # print host_b
    # print guest_b
    for i in range(0, len(liss)):
        final['a_liansai_total_' + liss[i]] = total_a[i]
        final['a_liansai_host_' + liss[i]] = host_a[i]
        final['a_liansai_guest_' + liss[i]] = guest_a[i]
        final['b_liansai_total_' + liss[i]] = total_b[i]
        final['b_liansai_host_' + liss[i]] = host_b[i]
        final['b_liansai_guest_' + liss[i]] = guest_b[i]


def game_basic_info(browser, final):
    ho = "//div[@class='odds_hd_cont']/table/tbody/tr/td[1]/ul/li"
    lis = browser.find_elements_by_xpath(ho)
    full_host_name = ''
    tprint(lis)
    if len(lis) > 1:
        full_host_name = lis[0].text
        tprint("host_name:", full_host_name)
        rank = lis[1].text
        n1 = rank.find(':')
        try:
            b = rank.find(' ')
            n2 = rank.index(':', n1 + 1)
            host_last_rank = rank[n1 + 1: b]
            # print host_last_rank
            host_rank = rank[n2 + 1:]
        except:
            host_last_rank = rank[n1 + 1:]
            host_rank = ''
            # print host_name, host_last_rank, host_rank
    else:
        host_name = lis[0].text
        host_last_rank = 0
        host_rank = 0
        # print host_name, host_last_rank, host_rank
    final['full_host_name'] = full_host_name
    final['host_last_rank'] = host_last_rank
    final['host_rank'] = host_rank
    center = "//div[@class='odds_hd_cont']/table/tbody/tr/td[3]/div"
    gameinfo = browser.find_element_by_xpath(center).text
    print("game:", gameinfo)
    # print game
    n1 = gameinfo.find('\n')
    n2 = gameinfo.find('\n', n1 + 1)
    n3 = gameinfo.find(':', n2)
    # print n1,n2,n3
    # print game
    nameround = gameinfo[:n1]
    di = nameround.find('第')
    lun = nameround.find('轮')
    game_name = nameround[:di]
    round = nameround[di + 1:lun]
    game_time = gameinfo[n1 + 5: n2]
    game_year = game_time[:game_time.find("-")]
    host_score = gameinfo[n2 + 1: n3]
    guest_score = gameinfo[n3 + 1:]
    # print 'n', round, 't', game_time, 'h', host_score, 'g', guest_score
    final['year'] = game_year
    final['game_name'] = game_name
    final['round'] = round
    final['game_time'] = game_time
    final['host_score'] = host_score
    final['guest_score'] = guest_score

    gu = "//div[@class='odds_hd_cont']/table/tbody/tr/td[5]/ul/li"
    lis = browser.find_elements_by_xpath(gu)
    tprint("guestname is", lis)
    if len(lis) > 1:
        full_guest_name = lis[0].text
        rank = lis[1].text
        n1 = rank.find(':')
        try:
            b = rank.find(' ')
            n2 = rank.index(':', n1 + 1)
            guest_rank = rank[n1 + 1: b]
            guest_last_rank = rank[n2 + 1:]
        except:
            guest_last_rank = rank[n1 + 1]
            guest_rank = ''
            # print guest_name, guest_last_rank, guest_rank
    else:
        full_guest_name = lis[0].text
        guest_rank = 0
        guest_last_rank = 0
        # print guest_name, guest_last_rank, guest_rank
    final['full_guest_name'] = full_guest_name
    final['guest_last_rank'] = guest_last_rank
    final['guest_rank'] = guest_rank

def get_team_info(browser):
    teamrank = {}
    i = 0
    try:
        xpath = "//div[@id='odds_nav_jfb']"
        teaminfomenu = browser.find_element_by_xpath(xpath)
        teaminfomenu.click()
    except:
        return None
    while True:
        i += 1
        xpath = "//div[@id='odds_nav_jfb']/div[@id='nav_jifen']/table/tbody/tr[%s]/td[2]"%i
        try:
            teaminfo = browser.find_element_by_xpath(xpath).text
            # tprint("teaminfo", teaminfo)
            if teaminfo:
                teamrank[teaminfo]  = i
            else:
                break
        except:
            # tprint("cannot find the xpath of %s" %xpath)
            break
    # tprint(teamrank)
    return teamrank

def get_basic_info(begin, end, cols=sd.COLUMNNAME, rowcount=1, ids=None):
    # oridata = pd.read_excel(TEMPBOOK)
    # oridata.columns = cols
    wb, st = getworkbook()
    writecolumns(wb, st)
    # writexls(wb, st, data=oridata)
    # olen = len(oridata)
    # if rowcount == None:
    #     rowcount = olen + 1
    #     print("Row number begin with %s" % rowcount)
    alldata = []
    # idlist = []
    if begin == -1 and ids:
        idlist = ids
    else:
        idlist = range(begin, end)
    # rowcount = 1

    for idd in idlist:
        try:
            url1 = r'http://odds.500.com/fenxi/shuju-%s.shtml' % str(idd)
            print(idd)
            data = get_js_basic(url1, idd)
            # print(data)
            if data != None:
                alldata.append(data)
                appendxls(wb,st,cols=cols, rowcount=rowcount,data=data)
                rowcount += 1
            time.sleep(2)
            if rowcount % 500 == 0:
                time.sleep(600)
        except:
            print("something error in %s"%idd)
            continue
    return alldata

# 获取网页中的赔率代码：
def get_js_peilv(url, idd):
    final = {}
    broswer = webdriver.PhantomJS()
    broswer.get(url)
    tprint(url)

    for i in range(1, 6):
        tr = "//table[@id='datatb']/tbody/tr[%s]" % str(i)
        tr_id = broswer.find_element_by_xpath(tr).get_attribute('id')
        if tr_id == '293' or tr_id == '2' or id == '5' or tr_id == '3' or tr_id == '4':
            tds = "//table[@id='datatb']/tbody/tr[%s]/td[3]/table/tbody/tr[1]/td" % str(i)
            lis = broswer.find_elements_by_xpath(tds)
            lii = []
            for li in lis:
                lii.append(li.text)
            tds = "//table[@id='datatb']/tbody/tr[%s]/td[4]/table/tbody/tr[1]/td" % str(i)
            lis = broswer.find_elements_by_xpath(tds)
            liis = []
            for li in lis:
                liis.append(li.text[:-1])
            tds = "//table[@id='datatb']/tbody/tr[%s]/td[7]/a[3]" % str(i)
            a = broswer.find_element_by_xpath(tds)
            he = a.get_attribute('href')
            broswer.get(he)
            allnum = broswer.find_element_by_id('allnum').text
            winnum = broswer.find_element_by_id('winnum').text
            drawnum = broswer.find_element_by_id('drawnum').text
            lostnum = broswer.find_element_by_id('lostnum').text
            break

    final['willian_win_rate'] = 1.0 * float(liis[0]) / 100.0
    final['willian_draw_rate'] = 1.0 * float(liis[1]) / 100.0
    final['willian_lost_rate'] = 1.0 * float(liis[2]) / 100.0
    final['peilv_id'] = idd
    final['weilian_win'] = lii[0]
    final['weilian_draw'] = lii[1]
    final['weilian_lost'] = lii[2]
    final['allnum'] = allnum
    final['winnum'] = winnum
    final['drawnum'] = drawnum
    final['lostnum'] = lostnum

    tprint(final)
    return final

# def get_js_ouzhi(url, idd):
#     final = {}
#     broswer = webdriver.PhantomJS()
#     broswer.get(url)
#     tprint(url)
#     ouzhipattern = "//div[@class='odds_content']/div[@id='table_top']/div[@class='odds_t']/table/tbody/tr[2]/th[7]/a"
#     ouzhiaction = broswer.find_element_by_xpath(ouzhipattern)
#     tprint(ouzhiaction.text)

def get_ouzhi_excel(url1,idd):
    r = rst.get(url1, stream=True)
    f = open("ozhidata//%s.xls"%idd, "wb")
    for chunk in r.iter_content(chunk_size=512):
        if chunk:
            f.write(chunk)
    f.close()

def get_ouzhi_info(begin, end):
    #http://odds.500.com/fenxi/europe_xls.php?fixtureid=706677
    for idd in range(begin, end):
        try:
            url1 = r'http://odds.500.com/fenxi/europe_xls.php?fixtureid=%s&excelst=0' %idd
            print(url1)
            get_ouzhi_excel(url1,idd)
            time.sleep(2)
        except:
            print("error in %s" %idd)
            continue
    return None

def process_ouzhi_excel(idd, fname):
    data = pd.read_excel(fname)
    data.columns = ['name','ousheng','ouping','oufu','oushenglv','oupinglv','oufulv','oufanhuanlv','kailisheng','kailiping','kailifu']
    data = data[5:]
    precolumnname = list(data['name'])
    newcolumnname = [a + "_" + b for a in precolumnname for b in data.columns if b != 'name']

    newdata = data.iloc[:,1:]

    newdata = pd.DataFrame(newdata.values.reshape(1,-1))
    newdata.columns = newcolumnname
    newdata['idd'] = idd
    result = newdata.to_dict(orient='records')
    return result[0]

def process_ouzhi_info(dirname):
    d = os.listdir(dirname)
    for each in d:
        if each.endswith(".xls"):
            idd = each[:each.rfind(".xls")]
            fname = os.path.join(dirname, each)
            print(fname)
            process_ouzhi_excel(idd, fname)
            break

def get_info(info, begin=0, end=0):
    if info == "basic":
        print("get the basic info")
        data = get_basic_info(begin, end)
    elif info == "ouzhi":
        print("get the ouzhi info.")
        data = get_ouzhi_info(begin, end)
    # for idd in range(begin, end):  # (624126, 624231):
    #     url1 = r'http://odds.500.com/fenxi/ouzhi-%s.shtml' % str(idd)
    #     try:
    #         print(idd)
    #         data = get_js_ouzhi(url1, idd)
    #     except:
    #         print("Unexpected error:", sys.exc_info()[0])

def main():
    data = get_info("basic",90355, 888888)
    # ids = [712899]
    # ids = [712331,712333,712334,708722,708719,708720,708721,712895,712894,712896,712899,712897,712898,712900,  673115,673420,673418,690233,687672,664972,665528,665532,665535,665531,665530,665536,665537,665534]




# 主函数
if __name__ == '__main__':
    main()
