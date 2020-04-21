import sys
import os
from selenium import webdriver
import time
import threading

browser = webdriver.Chrome()
#估值模型
# browser.get('https://www.touzid.com/company/dnp.html#/sh000651')
g_url = 'https://www.touzid.com/company/dnp.html#/sh600585'
browser.get(g_url)

def url_change_action():
    if g_url == 'https://www.touzid.com/':
        return
    browser.execute_script('var box = document.getElementsByClassName("el-popup-parent--hidden");\
        if(box && box[0] && box[0].style)\
            box[0].style.height = "100%";\
            box[0].style.overflow = "scroll";\
        var v = document.getElementsByClassName("v-modal");\
        if(v && v[0] && v[0].style)\
            v[0].style.display = "none";\
        var b = document.getElementsByClassName("el-dialog");\
        if(b && b[0] && b[0].style)\
            b[0].style.display = "none";\
        var c = document.getElementsByClassName("el-dialog__wrapper");\
        if(c && c[0] && c[0].style)\
            c[0].style.display = "none"')

    # browser.execute_script('var box = document.getElementsByClassName("el-popup-parent--hidden");\
    #     box[0].style.height = "100%";\
    #     box[0].style.overflow = "scroll";')

    # element = browser.find_elements_by_class_name('cell')
    # buy_price = 0
    # cur_price = 0
    # for i in range(len(element)):
    #     # print(element[i].text)
    #     if element[i].text == '合理买入价格':
    #         buy_price = element[i + 1].text
    #     if element[i].text == '当前价格':
    #         cur_price = element[i + 1].text
    #     if buy_price != 0 and cur_price != 0:
    #         break
    # print(buy_price)
    # print(cur_price)

def main():
    global g_url
    # button = browser.find_element_by_xpath('//*[@id="form"]/span[1]')
    url_change_action()
    while True:
        time.sleep(5)
        url = browser.current_url
        if url != g_url:
            g_url = url
            url_change_action()
            print(url)

    return

if __name__ == "__main__":
    main()