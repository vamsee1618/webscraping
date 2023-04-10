from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
from time import sleep
import pandas as pd
from datetime import date
from tqdm import tqdm, notebook
import json
import re
import numpy as np
import random 
tqdm.pandas()


def driver_launcher():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    time.sleep(random.randint(3,5))
    return driver

def glassdoor_soup(job_soup):
    def _has_no_attrs(tag):
        return tag.name == 'script' and not tag.attrs     

    js = job_soup.find(_has_no_attrs).text.replace("window.appCache=", "").replace(";", "")        
    json_script = json.loads(js)

    job_dict = {}

    try:
        job_dict['role'] = job_soup.select_one("div[data-test='job-title']").find(text = True)
    except:
        pass

    try:
        job_dict['posted_date'] = json_script["initialState"]["jlData"]['job']['discoverDate']
    except:
        pass

    try:
        job_dict['company'] = job_soup.select_one("div[data-test='employer-name']").find(text = True)
    except:
        pass    

    try:
        job_dict['location'] = job_soup.select_one("span[data-test='location']").find(text = True)
    except:
        pass 

    try:
        job_dict['salary_est'] = job_soup.select_one("span.small.css-10zcshf.e1v3ed7e1").find(text = True, recursive = False)
    except:
        pass

    try:
        job_dict['education'] = json_script["initialState"]["jlData"]["header"]["indeedJobAttribute"]["educationLabel"][0]
    except:
        pass

    try:
        job_dict['skills'] = json_script["initialState"]["jlData"]["header"]["indeedJobAttribute"]["skillsLabel"]
    except:
        pass

    try:
        job_dict['year_exp'] = json_script["initialState"]["jlData"]["header"]["indeedJobAttribute"]["yearsOfExperienceLabel"][0]
    except:
        pass

    try:
        job_dict['job_description'] = re.sub("<.*?>", " ", json_script["initialState"]["jlData"]["job"]["description"])
    except:
        pass

    return job_dict

def search_jobs(job_title,job_location,last_days):
    job_title=job_title
    job_location=job_location
    driver = driver_launcher()
    driver_job = driver_launcher()  


    driver.get("https://www.glassdoor.com/Job/")
    time.sleep(random.randint(3,5))

    job_title=job_title
    job_location=job_location

    job_search_element = driver.find_element(By.ID, "sc.keyword")
    job_search_element.clear()
    job_search_element.send_keys(job_title)

    time.sleep(random.randint(3,5))
    job_location_element = driver.find_element(By.ID, "sc.location")
    job_location_element.clear()
    job_location_element.send_keys(job_location)
    job_location_element.send_keys(Keys.RETURN)

    time.sleep(random.randint(3,5))
    get_url = driver.current_url
    new_url = get_url+'&jobType=fulltime'+'&fromAge={}'.format(last_days)
    driver.get(new_url)

    no_pages_full = driver.find_element(By.CLASS_NAME,"paginationFooter").text
    no_pages      = int(re.search(r'of\s(\d+)', no_pages_full).group(1))

    job_list = []
    print("Pages:{}".format(no_pages))
    for page in tqdm(range(1,no_pages+1)): 

        time.sleep(random.randint(5,10))
        try:
            driver.find_element(By.XPATH,("//span[@alt='Close']")).click()
        except:
            pass    

        time.sleep(random.randint(2,3))

        job_buttons = driver.find_elements(By.CSS_SELECTOR, "a.jobLink.css-1rd3saf.eigr9kq2")

        button_count = 0
        
        for button in job_buttons:          
            try:
                driver.find_element(By.XPATH,("//span[@alt='Close']")).click()
            except:
                pass
            time.sleep(random.randint(2,3))

            button.click() 
            detail_page_url = button.get_attribute("href")            

            time.sleep(random.randint(3,5))
            driver_job.get(detail_page_url)

            html = driver_job.page_source
            job_soup = BeautifulSoup(html, 'html.parser')
            job_dict = glassdoor_soup(job_soup)
            job_list.append(job_dict)
            
            time.sleep(random.randint(3,5))   

        df_jobs = pd.DataFrame(job_list)
        df_jobs['job_role_input'] = job_title
        df_jobs['job_location_input'] = job_location
        
        # Save file for every page    
        df_jobs.to_excel("glassdoor_jobs_data_{}_{}_{}.xlsx".format(job_title,job_location,date.today()))
        next_button = driver.find_element(By.CSS_SELECTOR, "button.nextButton.css-1hq9k8.e13qs2071").click()
    driver.quit()
    driver_job.quit()
    return df_jobs      