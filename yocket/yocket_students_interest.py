"""
Heavy usage of pandas
Yocket Webscraping 

Note: Only for the analysis
"""
## Import required libraries
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from time import sleep
import json

import pandas as pd
import urllib.parse
from tqdm import tqdm, notebook
from datetime import date
import datetime
from tqdm import tqdm
import pickle
import re
import mysql.connector
from sqlalchemy import create_engine
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
from gspread_dataframe import set_with_dataframe
my_conn = create_engine(input("Enter the Mysql Engine URL:"))
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


todays_date = date.today()
current_year = todays_date.year


total_aspirants = {}

driver.get("https://yocket.com/connect?country=United%20States&term=Fall&year={}".format(current_year))
time.sleep(10)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
total_value = soup.find('p',"text-gray-700").text.strip()
total_aspirants[current_year] = total_value


df_usa_aspirants = pd.DataFrame.from_dict(total_aspirants.items())
df_usa_aspirants.rename(columns={0: 'year', 1:'student_count_text'},inplace=True)
df_usa_aspirants['student_count'] = df_usa_aspirants['student_count_text'].str[19:].str.split('aspirant').str[0].astype(int)
df_usa_aspirants['year'] = df_usa_aspirants['year'].astype(int)
df_usa_aspirants['date_timestamp'] = date.today()

df_usa_aspirants.to_sql(con=my_conn,name='yearly_highlevel_data',if_exists='append',index=False)

total_aspirants_ba = {}

driver.get("https://yocket.com/connect?course=Business%20Analytics&country=United%20States&term=Fall&year={}".format(current_year))
time.sleep(10)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
total_value = soup.find('p',"text-gray-700").text.strip()
total_aspirants_ba[current_year] = total_value



df_msba_aspirants = pd.DataFrame.from_dict(total_aspirants_ba.items())
df_msba_aspirants.rename(columns={0: 'year', 1:'student_count_text'},inplace=True)
df_msba_aspirants['student_count'] = df_msba_aspirants['student_count_text'].str[19:].str.split('aspirant').str[0].astype(int)
df_msba_aspirants['year'] = df_msba_aspirants['year'].astype(int)
df_msba_aspirants['date_timestamp'] = date.today()


df_msba_aspirants.to_sql(con=my_conn,name='yearly_msba',if_exists='append',index=False)
school_id_dict = {}
school_id_dict[868]  = 'University of California, Davis'
school_id_dict[713]  = 'University of Texas, Austin (McCombs)'
school_id_dict[707]  = 'University of California, Los Angeles (Anderson)'
school_id_dict[745]  = 'University of Southern California (Marshall)'
school_id_dict[1480] = 'University of Washington (Foster)'
school_id_dict[702]  = 'Carnegie Mellon University (Tepper)'
school_id_dict[748]  = 'Purdue University, West Lafayette (Krannert)'
school_id_dict[709]  = 'Columbia University'
school_id_dict[764]  = 'University of California, San Diego'
school_id_dict[1094] = 'University of Minnesota, Twin Cities (Carlson)'
school_id_dict[2833] = 'University of San Francisco (Masagung)'
school_id_dict[743]  = 'University of Cincinnati'
school_id_dict[711]  = 'University of Illinois--Urbana-Champaign'
school_id_dict[1104]  = 'University of Connecticut'
school_id_dict[782]  = 'Arizona State University'
school_id_dict[1103]  = 'George Washington University'
school_id_dict[810]  = 'University of Illinois--Chicago (Liautaud)'
school_id_dict[2638]  = 'University of Illinois--Chicago (Liautaud)'


school_year_wise_aspirants = []
for uni in tqdm(school_id_dict.keys()):
    applicant = {}
    applicant['year'] = current_year
    applicant['university'] = school_id_dict[uni]
    driver.get("https://yocket.com/connect?university={}&course=Business%20Analytics&country=United%20States&term=Fall&year={}".format(uni,current_year))
    time.sleep(10)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    value = soup.find('p',"text-gray-700").text.strip()
    applicant['student_count_text'] = value
    school_year_wise_aspirants.append(applicant)


df_school_year = pd.DataFrame(school_year_wise_aspirants)
df_school_year['student_count'] = df_school_year['student_count_text'].str[19:].str.split('aspirant').str[0].astype(int)
df_school_year['year'] = df_school_year['year'].astype(int)
df_school_year['date_timestamp'] = date.today()


df_school_year.to_sql(con=my_conn,name='uni_msba',if_exists='append',index=False)


def categorise(x):  
    if (x['year'] == 2023) and (x['date_timestamp'] == max(df_sheet1['date_timestamp'])):
        return True
    elif (x['year'] < 2023) :
        return True
    else:
        return False

driver.close()




