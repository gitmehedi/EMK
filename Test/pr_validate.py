import time
from select import select
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import keys
driver=webdriver.Firefox(executable_path="F:\Selenium\geckodriver")
driver.get("http://192.168.1.105:8060/web/database/selector")
time.sleep(2)
driver.find_element_by_xpath("html/body/div[1]/div/div[2]/a[3]").click()
element=driver.find_element_by_id("login").send_keys("utpal_chem@scclbd.com")
element=driver.find_element_by_id("password").send_keys("@dminsccl")
time.sleep(2)
driver.find_element_by_xpath("/html/body/div/main/div/form/div[4]/button").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[1]/li[3]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[3]/ul[1]/li[2]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div/table/tbody/tr[1]/td[2]").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/header/button[6]/span").click()
time.sleep(2)
element=driver.find_element_by_id("o_field_input_34").click()
element=driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div/div/div/table[1]/tbody/tr/td[2]/select/option[3]").click()
element=driver.find_element_by_id("o_field_input_35").click()
#drp=select(element)
time.sleep(2)
#drp.select_by_index('1')