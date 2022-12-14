import time
from select import select
from selenium import webdriver
from selenium.webdriver.common.keys import keys
#from Dropdown import element
driver=webdriver.Firefox(executable_path="F:\Selenium\geckodriver")
driver.get("https://www.phptravels.net")
time.sleep(2)
driver.find_element_by_xpath("/html/body/header/div[2]/div/div/div/div/div[2]/nav/ul/li[5]/a").click()
time.sleep(2)
element=driver.find_element_by_css_selector("#select2-to_country-container").click()
time.sleep(2)
drp=select(element)
drp.select_by_index('4')
#drp.select_by_visible_text('Legoland Malaysia Day pass')
time.sleep(5)
driver.close()


time.sleep(2)
time.sleep(2)
