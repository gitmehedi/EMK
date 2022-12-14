import time
from select import select
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import keys
from selenium.webdriver.common.keys import keys
driver=webdriver.Firefox(executable_path="F:\Selenium\geckodriver")
driver.get("https://www.phptravels.net")
time.sleep(2)
driver.find_element_by_xpath("/html/body/section[1]/div/div/div/div/div[2]/ul/li[3]/button/span[2]").click()