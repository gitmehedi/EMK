import time
from select import select
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import keys
from selenium.webdriver.common.keys import keys
driver=webdriver.Firefox(executable_path="F:\Selenium\geckodriver")
driver.get("https://gen-bizbd.com/web/login")
time.sleep(2)
element=driver.find_element_by_id("login").send_keys("ma.zaman@scclbd.com")
element=driver.find_element_by_id("password").send_keys("dfsdfsdg")
time.sleep(2)
driver.find_element_by_xpath("/html/body/div/main/div/form/div[3]/button").click()
time.sleep(7)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[1]/li[3]/a/span").click()
time.sleep(4)