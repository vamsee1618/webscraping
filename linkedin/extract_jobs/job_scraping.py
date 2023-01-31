"""
Extract Full-Time jobs and extract the relevant info
Provide either Keywords or Data Science/Analytics related job titles
Feel free to add other titles and their respective ids which can be found in the URL

Requirements:
    Selenium Driver

Note: Use only for analysis
"""
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
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
tqdm.pandas()

### Job Title Dictionary - Titles and IDs
job_title_dictionary = {"Data Analyst":"340","Senior Data Analyst":"2463","Business Analyst":"29",
                        "Senior Business Analyst":"194","Product Manager":"27","Senior Product Manager":"270",
                       "Project Manager":"4","Senior Project Manager":"77","Data Engineer":"2732",
                       "Data Scientist":"25190","Senior Data Scientist":"25887","Machine Learning":"25206",
                       "Lead Data Scientist":"25885","Data Science Manager":"30009","Analytics Specialist":"30209",
                       "Data Associate":"7443","Business Intelligence Developer":"3282",
                        "Business Intelligence Analyst":"2336"}


class LinkedInJobScraper:
    def __init__(
                 self, 
                 job_title_dictionary=job_title_dictionary, 
                 keywords=None, 
                 job_list=['Data Analyst','Senior Data Analyst','Business Analyst','Senior Business Analyst','Data Scientist','Senior Data Scientist'], 
                 job_location='California', 
                 job_period="&f_TPR=r604800", 
                 geo_id=None, 
                 experience_level=None,
                 filename='all_jobs'
                ):
        self.job_title_dictionary = job_title_dictionary
        self.keywords             = keywords
        self.job_list             = job_list
        self.job_location         = job_location
        self.job_period           = job_period
        self.geo_id               = geo_id
        self.experience_level     = experience_level
        self.filename             = filename
        self.url                  = None
   
    def url_gen(self):
        """
        Generates a URL for searching jobs on LinkedIn based on the provided parameters.
        
        Input parameters:
            keywords             -  Provide the job word in a string format
            job_title_dictionary -  URLs Titles and IDs Dictionary to target specific job titles
            job_list             -  List of the Jobs, Refer to the List of Jobs Provided
            job_location         -  Provide the target job location, default United States
            job_period           -  Provide the time period you want for, default weekly
            geo_id               -  Provide the geo id if you want specific location
            experience           -  Entry, Associate, Mid-Senior, Director
            filename             -  Provide the filename to be saved
        
        Output:
            URL to search
        """
        try:
            ### base url for job search
            url = 'https://www.linkedin.com/jobs/search/?f_JT=F'

            ### specific inputs
            period = self.job_period
            
            ### Applying the job titles filter
            if self.job_list:
                job_string = self.job_title_dictionary[self.job_list[0]]
                if len(self.job_list)>1:
                    for i in range(1,len(self.job_list)):
                        job_string += '%2C' + self.job_title_dictionary[self.job_list[i]]
                job_ids = '&f_T=' + job_string
                url+= job_ids 
            
            if self.keywords:
                keywords = '&keywords=' + urllib.parse.quote(self.keywords)
                url+= keywords
            
            if self.job_location:
                location = "&location=" + urllib.parse.quote(self.job_location)
            else:
                location = "&location=" + "United%20States"

            if self.experience_level:
                if self.experience_level == "Entry":
                    exp = '&f_E=' + str(2)
                elif self.experience_level == "Associate":
                    exp = '&f_E=' + str(3)
                elif self.experience_level == "Mid-Senior":
                    exp = '&f_E=' + str(4)
                elif self.experience_level == "Director":
                    exp = '&f_E=' + str(5)
                url+= exp 
            
            if self.geo_id:
                geo = "&geoId=" + str(geo_id)
                url += geo
            else:
                geo = ""
            url += period + location
            
            # To distinguish Washington state from Washington DC
            if self.geo_id:
                url = url + "&geoId={}".format(geo_id)
            elif self.job_location == "Washington":
                url = url + "&geoId=103977389"
            elif self.job_location == "San Francisco Bay Area":
                url = url + "&geoId=90000084"
            elif self.job_location == "Los Angeles Metropolitan Area":
                url = url + "&geoId=90000049"
            
            self.url = url
                
        except Exception as e:
            print("Error generating URL: ", e)
        return self.url
    
    def close_browser(self):
        """
        Closes the web driver.
        """
        self.driver.quit()
    
    def scrape_jobs(self,driver):
        """
        Scrapes job information from the provided LinkedIn job search URL.

        Input parameter:
            url - LinkedIn job search URL

        Output:
            scraped job data
        """
        try:
            driver.get(self.url) ### Driver get the URL
            time.sleep(5)
            job_data = []
            try:
                ### Total Number of Pages
                total_page_elements = driver.find_elements(By.CLASS_NAME,'artdeco-pagination__indicator--number')
                total_pages = int(total_page_elements[-1].text)
            except:
                total_pages = 1
                pass
           
            ## Load each page
            page_num = 0
            job_text_list = []
            
            ## Iterate overall pages
            for i in range(total_pages):
                job_search_url_page = self.url + '&start={}'.format(page_num) 
                driver.get(job_search_url_page)
                time.sleep(10)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                job_linkedin_url = 'https://www.linkedin.com/'
                ## Get all the jobids
                job_id_list = [tag['data-occludable-job-id'] for tag in soup.select('li.scaffold-layout__list-item')]
                # Find all the elements within the job container
                total_job_elements = driver.find_elements(By.CLASS_NAME,'scaffold-layout__list-item')
                print("job_element in page {}".format(i+1))
                job_id_num = 0
                
                ## Iterate over all the jobs and extract info
                for job_element in tqdm(total_job_elements):
                    job_element.click()
                    time.sleep(10)
                    job_text_dict = {}
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    ## extract relevant info
                    try:
                        job_text_dict['job_url'] = job_linkedin_url + soup.select("div.jobs-unified-top-card__content--two-pane")[0].find("a").get("href")
                    except:
                        pass
                    try:
                        job_text_dict['job_id'] = job_id_list[job_id_num]
                        job_id_num+=1
                    except:
                        pass
                    try:
                        job_text_dict['job_title']        = soup.select("div.jobs-unified-top-card__content--two-pane")[0].find('h2').text.strip()
                    except:
                        pass
                    try:
                        job_text_dict['job_company_name'] = soup.select('span.jobs-unified-top-card__company-name')[0].text.strip()
                    except:
                        pass
                    try:
                        job_text_dict['job_location']     = soup.select('span.jobs-unified-top-card__bullet')[0].text.strip()
                    except:
                        pass
                    try:  
                        job_text_dict['job_posted']       = soup.select('span.jobs-unified-top-card__posted-date')[0].text.strip()
                    except:
                        pass
                    try:
                        job_text_dict['job_key_details']  = soup.select('div.jobs-unified-top-card__content--two-pane')[0].find('ul').text.strip()
                    except:
                        pass
                    try:
                        job_text_dict['job_description']  = soup.select("div.jobs-description-content")[0].text.strip()
                    except:
                        pass
                    try:
                        job_text_dict['job_text']         = soup.select("div.jobs-details")[0].text
                    except:
                        pass
                    time.sleep(5)
                    job_text_dict['job_posting_type'] = self.job_list
                    job_text_dict['run_date'] = datetime.now()
                    job_text_list.append(job_text_dict)
                    df_jobs = pd.DataFrame(job_text_list)
                # Save file for every page    
                df_jobs.to_excel("jobs_data_{}_{}.xlsx".format(self.filename,date.today()))
                page_num += 25 ## For every page there are 25 jobs
                time.sleep(3)
            print('Process-Ended')
            self.close_browser()
        except Exception as e:
             print(e)                                  
        return df_jobs  
    
class dataframe_cleaning:
    def __init__(self):
        pass
    
    # Function to extract the salary range
    def extract_salary(self,text):
        match = re.search(r'\$\d+,\d+/yr - \$\d+,\d+/yr', text)
        if match:
            return match.group()
        else:
            return "0"
    
    ## Function to extract the qualifications out of the job description
    def extract_qualifications(self,x):
        quali = ''
        if x is None:
            pass
        else:
            list_texts = x.split('\n')
            quali = ''
            for i in list_texts:
                if 'degree' in i.lower() or 'years of experience' in i.lower():
                    quali+=i

        return quali
    
    ## Function to extract the years of experience from the job description
    def extract_years_of_experience(self,x):
        match = re.search(r'\d+\s*-\s*\d+\s*years? of experience', x)
        if match:
            return match.group()
        match = re.search(r'\d+\s*years? of experience', x)
        if match:
            return match.group()
        match = re.search(r'\d+\+? years', x)
        if match:
            return match.group()
        return None
    
    ## Function to extract the job postdate
    def extract_post_date(self,row):
        if row['job_posted'] and not pd.isnull(row['job_posted']):
            match = re.search(r'\d+', row['job_posted'])
            number = int(match.group())
            if "day" in row['job_posted']:
                post_date = row['run_date'] - timedelta(days=number)
            elif "week" in row['job_posted']:
                post_date = row['run_date'] - timedelta(weeks=number)
            elif "hour" in row['job_posted']:
                post_date = row['run_date'] - timedelta(hours=number)
            elif "minute" in row['job_posted']:
                post_date = row['run_date'] - timedelta(minutes=number)
            elif "second" in row['job_posted']:
                post_date = row['run_date'] - timedelta(seconds=number)
            else:
                post_date = row['run_date']
        else:
            post_date = row['run_date']
        return post_date
    
    ## extract the essential info and apply the functions defined above
    def extract_required_info(self,df_jobs):
    
        df_jobs['no_of_applicants'] = df_jobs['job_key_details'].str.replace(',','').str.extract(r'See how you compare to (\d+) applicants')
        df_jobs['role_types']       = df_jobs['job_key_details'].str.extract(r'(Full-time) (.+?)\n')[1]
        df_jobs.loc[df_jobs['job_key_details'].notna(), 'salary_range'] = df_jobs.loc[df_jobs['job_key_details'].notna(), 'job_key_details'].apply(self.extract_salary)
        df_jobs['industry'] = df_jobs['job_key_details'].str.extract(r'employees · (.*?)\n')
        df_jobs['job_description'] = df_jobs['job_description'].fillna('')
        df_jobs['qualification'] = df_jobs['job_description'].apply(lambda x: self.extract_qualifications(x))
        df_jobs['experience'] = df_jobs['qualification'].apply(self.extract_years_of_experience)
        df_jobs['job_postdate'] =df_jobs.apply(lambda x: self.extract_post_date(x),axis=1)
        return df_jobs

    

if __name__ == "__main__":
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    time.sleep(5)
    driver.get("https://www.linkedin.com/login")
    # Find and input email
    time.sleep(3)
    email = driver.find_element(By.ID, "username")
    user_name = input("Please provide user name:")
    email.send_keys(user_name)
    time.sleep(3)
    # Find and input password
    password = driver.find_element(By.ID, "password")
    time.sleep(3)
    linkedin_password = input("Please provide password:")
    password.send_keys(linkedin_password)
    password.send_keys(Keys.RETURN)
    time.sleep(3)
    scraping_class=LinkedInJobScraper()
    url = scraping_class.url_gen()
    df_jobs = scraping_class.scrape_jobs(driver)
    dataframe_cleaning_class = dataframe_cleaning()
    df_final = dataframe_cleaning_class.extract_required_info()
    
    
    
