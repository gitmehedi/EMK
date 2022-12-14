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
element=driver.find_element_by_id("login").send_keys("rafsansheikh@yahoo.com")
element=driver.find_element_by_id("password").send_keys("@dminsccl")
time.sleep(2)
driver.find_element_by_xpath("/html/body/div/main/div/form/div[4]/button").click()
time.sleep(5)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[1]/li[3]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[3]/ul[4]/li[1]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/div/button[1]").click()
time.sleep(2)
driver.find_element_by_id("o_field_input_8").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/ul/li[3]/a").click()
time.sleep(2)
# Operating unit select
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[2]/div[2]/table/tbody/tr[1]/td/a").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[2]/div[1]/div[1]/div/input").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/ul[2]/li[4]/a").click()
# Customer select
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[2]/div[1]/div[2]/div/input").click()
driver.find_element_by_xpath("/html/body/ul[3]/li[1]/a").click()
driver.find_element_by_css_selector("input.o_form_input:nth-child(7)").click()

# give schedule qty
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[2]/div[1]/input").clear()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[2]/div[2]/table/tbody/tr[1]/td[7]").click()
time.sleep(2)
# driver.find_element_by_css_selector("input.o_form_input:nth-child(7)").clear()
# time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div/div/div/div[1]/div/div[2]/div[1]/input").send_keys(10)
# time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/header/button[1]/span").click()
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/div/div[2]/button[1]").click()