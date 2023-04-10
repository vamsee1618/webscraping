import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import time
from time import sleep
import math
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta
from datetime import date
from tqdm import tqdm, notebook
from itertools import product
import re
import pprint
import numpy as np
import random 
tqdm.pandas()

def driver_launcher(username,password):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    time.sleep(5)
    driver.get("https://www.linkedin.com/login")
    # Find and input email
    time.sleep(3)
    email = driver.find_element(By.ID, "username")
    user_name = username
    email.send_keys(user_name)
    time.sleep(3)
    # Find and input password
    user_password = driver.find_element(By.ID, "password")
    time.sleep(3)
    linkedin_password = password
    user_password.send_keys(linkedin_password)
    time.sleep(3)
    user_password.send_keys(Keys.RETURN)
    time.sleep(5)
    driver.save_screenshot("login_screenshot.png")
    return driver

user_usernamelist = ["mosbyted914@gmail.com","ted20266@gmail.com","scherbatskyrobin784@gmail.com"]
user_passwordlist = ["Password@123","Password@123","scherrobin784"]

user=0

user_username=user_usernamelist[user]
user_password=user_passwordlist[user]
driver=driver_launcher(username=user_username,password=user_password)
time.sleep(30)