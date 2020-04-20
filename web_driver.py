import sys
import os
from selenium import webdriver
import time
import threading

browser = webdriver.Chrome()
#估值模型
# browser.get('https://www.touzid.com/company/dnp.html#/sh000651')
g_url = 'https://www.touzid.com/company/dnp.html#/sh603583'
browser.get(g_url)

def url_change_action():
    browser.execute_script('var box = document.getElementsByClassName("el-popup-parent--hidden");\
        box[0].style.height = "100%";\
        box[0].style.overflow = "scroll";\
        var v = document.getElementsByClassName("v-modal");\
        v[0].style.display = "none";\
        var b = document.getElementsByClassName("el-dialog");\
        b[0].style.display = "none";\
        var b = document.getElementsByClassName("el-dialog__wrapper");\
        b[0].style.display = "none"')

#     browser.execute_script('var script=document.createElement("script"); \
#     script.type="text/javascript"; \
#     script.src="https://code.jquery.com/jquery-1.12.4.min.js"; \
#     document.getElementsByTagName("head")[0].appendChild(script);\
#     var find = $("b").filter(function() {\
#     return $(this).html().trim() === "合理买入价格"\
#     });\
#     find.html(123123)')



def main():
    def fun_timer():
        global timer
        global browser
        global g_url
        url = browser.current_url
        print(browser.window_handles)
        if url != g_url:
            g_url = url
            url_change_action()
            print(url)
        timer = threading.Timer(2, fun_timer)
        timer.start()

    # timer = threading.Timer(5, fun_timer)
    # timer.start()
    # button = browser.find_element_by_xpath('//*[@id="form"]/span[1]')
    url_change_action()
    time.sleep(5000)
    return

if __name__ == "__main__":
    main()