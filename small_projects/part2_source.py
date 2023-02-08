import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import time
from fake_useragent import UserAgent
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56"}## Defining headers to avoid errors

def main():
    try:
        
        ### Part-2
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        time.sleep(5)

        driver.get("https://www.google.com/")
        time.sleep(5)

        search_key=driver.find_element(By.NAME,"q")
        
        
        search_key.send_keys("askew")
        time.sleep(5)
        search_key.send_keys(Keys.ENTER)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        print(soup.text)

        ### 2nd search
        search_key=driver.find_element(By.NAME,"q")
        search_key.clear()
        time.sleep(5)
        search_key.send_keys("google in 1998")
        time.sleep(5)
        search_key.send_keys(Keys.ENTER)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        print(soup.text)

        ### Best Buy
        driver.get("https://www.bestbuy.com/")
        time.sleep(10)

        deal_of_day = driver.find_element(By.LINK_TEXT, "Deal of the Day")
        deal_of_day.click()
        time.sleep(5)

        timeleft=driver.find_element(By.CLASS_NAME,"message")
        print(timeleft.text)
        time.sleep(5)

        reviews_click=driver.find_element(By.CLASS_NAME,"c-reviews ")
        reviews_click.click()

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        with open('bestbuy_deal_of_the_day.html', 'w', encoding="utf-8") as file:
            file.write(str(soup))
        
        driver.quit()
    
    except Exception as ex:
        print('error: ' + str(ex))

if __name__ == '__main__':
    main()

