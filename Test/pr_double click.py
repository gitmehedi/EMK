import time
from select import select
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import keys
driver=webdriver.Firefox(executable_path="F:\Selenium\geckodriver")
driver.get("http://192.168.1.105:8060/web/database/selector")
time.sleep(2)
driver.find_element_by_xpath("html/body/div[1]/div/div[2]/a[3]").click()
element=driver.find_element_by_id("login").send_keys("abdulhye.niloy@gmail.com")
element=driver.find_element_by_id("password").send_keys("@dminsccl")
time.sleep(3)
driver.find_element_by_xpath("/html/body/div/main/div/form/div[4]/button").click()
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[1]/li[3]/a/span").click()
time.sleep(3)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/div/button[1]").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[1]/td/a").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/div[1]/div[1]/div/input").click()
time.sleep(2)
element=driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/div[1]/div[1]/div/input")
#drp.select_by_visible_text('[10.01.013] Carbolic Acid (Admin)')
time.sleep(2)
driver.find_element_by_xpath("/html/body/ul[10]/li[1]/a").click()
time.sleep(2)