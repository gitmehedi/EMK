import time
from select import select
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import keys
driver=webdriver.Firefox(executable_path="F:\Selenium\geckodriver")
driver.get("http://192.168.1.105:8060/web/database/selector")
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/a[4]").click()
time.sleep(2)
element=driver.find_element_by_id("login").send_keys("nurnabi@scclbd.com")
element=driver.find_element_by_id("password").send_keys("@dminsccl")
time.sleep(4)
driver.find_element_by_xpath("/html/body/div/main/div/form/div[4]/button").click()
time.sleep(6)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[1]/li[7]/a/span").click()
time.sleep(6)
driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[7]/ul[1]/li[1]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div/table/tbody/tr[1]/td[2]").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/header/button[6]/span").click()
time.sleep(2)