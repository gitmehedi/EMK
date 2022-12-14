import time
from select import select
from selenium import webdriver
from selenium.webdriver import ActionChains
import selenium.webdriver.common.keys
driver=webdriver.Firefox(executable_path="E:\Selenium\geckodriver")
driver.get("http://192.168.1.105:8060/web/database/selector")
time.sleep(2)
element=driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/a[10]").click()
time.sleep(2)
element=driver.find_element_by_id("login").send_keys("rafsansheikh@yahoo.com")
element=driver.find_element_by_id("password").send_keys("@dminsccl")
time.sleep(2)
driver.find_element_by_xpath("/html/body/div/main/div/form/div[4]/button").click()
time.sleep(5)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[1]/li[3]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[3]/ul[1]/li[2]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/div/button[1]").click()
driver.find_element_by_id("o_field_input_6").click()
# Customer select
time.sleep(2)
driver.find_element_by_xpath("/html/body/ul[1]/li[4]/a").click()
driver.find_element_by_id("o_field_input_17").click()
# Type select
driver.find_element_by_xpath("/html/body/ul[4]/li[3]/a").click()
time.sleep(2)
driver.find_element_by_id("o_field_input_20").click()
# Packing mode select
driver.find_element_by_xpath("/html/body/div[7]/div/div/div[2]/div[2]/div/table/tbody/tr[13]/td").click()
time.sleep(2)
driver.find_element_by_id("o_field_input_21").click()
# Sales channel select
driver.find_element_by_xpath("/html/body/ul[6]/li[1]/a").click()
time.sleep(2)
driver.find_element_by_id("o_field_input_25").click()
driver.find_element_by_xpath("/html/body/ul[8]/li[6]/a").click()
# Payment Terms select
driver.find_element_by_id("radio52_non_vat").click()
#Is VAT Applicable
driver.find_element_by_id("radio53_non_bonded").click()
#Is Bonded Applicable
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[1]/td/a").click()
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/div[1]/div[1]/div/input").click()
driver.find_element_by_xpath("/html/body/ul[12]/li[1]/a").click()
# Product select
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/div[1]/input[1]").click()
driver.find_element_by_css_selector("input.o_form_input:nth-child(6)").clear()
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/div[1]/input[1]").send_keys("100")
time.sleep(5)
# Order Qty
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/div[2]/table/tbody/tr[1]/td[6]").click()
driver.find_element_by_css_selector("input.o_form_input:nth-child(14)").clear()
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/div[1]/input[3]").send_keys("1200")
# Unit price input
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/header/button[14]/span").click()
time.sleep(2)
# Submit
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[1]/div[2]/div[1]/div/div[2]/button[1]").click()
#Save
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[2]/li/a/span[2]").click()
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[2]/li/ul/li[3]/a").click()
time.sleep(2)
#logout
element=driver.find_element_by_id("login").send_keys("rony@scclbd.com")
element=driver.find_element_by_id("password").send_keys("@dminsccl")
time.sleep(2)
# Sales approval
driver.find_element_by_xpath("/html/body/div/main/div/form/div[4]/button").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[1]/li[3]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[3]/ul[1]/li[1]/a").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div/table/tbody/tr[1]/td[2]").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/header/button[15]").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[2]/li/a/span[2]").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[2]/li/ul/li[3]/a").click()
time.sleep(2)
#logout
element=driver.find_element_by_id("login").send_keys("ma.zaman@scclbd.com")
element=driver.find_element_by_id("password").send_keys("@dminsccl")
time.sleep(2)
driver.find_element_by_xpath("/html/body/div/main/div/form/div[4]/button").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[1]/li[3]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[3]/ul[1]/li[1]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div/table/tbody/tr[1]/td[2]").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/header/button[16]/span").click()
# Accounts approval
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[2]/li/a/span[2]").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[2]/li/ul/li[3]/a").click()
#logout
time.sleep(2)
element=driver.find_element_by_id("login").send_keys("das.bk.sccl@gmail.com")
element=driver.find_element_by_id("password").send_keys("@dminsccl")
time.sleep(2)
driver.find_element_by_xpath("/html/body/div/main/div/form/div[4]/button").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/nav/div[2]/ul[1]/li[3]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[1]/div[3]/ul[1]/li[1]/a/span").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/div/table/tbody/tr[1]/td[2]").click()
time.sleep(2)
driver.find_element_by_xpath("/html/body/div[1]/div[2]/div[2]/div/div/header/button[5]/span").click()
# CXO approval