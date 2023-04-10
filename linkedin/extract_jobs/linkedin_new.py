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
import pickle
from sqlalchemy import create_engine
tqdm.pandas()
my_conn = create_engine("mysql+mysqldb://root:sqlking1611@localhost/linkedin_scraping")


with open("skills_list", "rb") as fp:
    skills_list = pickle.load(fp)


class LinkedInJobScraper:
    """
    Fetches the details of the each job
    """
    def __init__(self):
        pass
   
    def url_gen(self, 
                 keywords=None, 
                 job_list=None, 
                 job_location='California', 
                 job_period="&f_TPR=r604800", 
                 geo_id=None, 
                 experience_level=None,
                 workplace_type=None
                 ):

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
            job_title_dictionary = {"Data Analyst":"340","Senior Data Analyst":"2463","Business Analyst":"29",
                        "Senior Business Analyst":"194","Analytics Manager":"2525","Product Manager":"27","Senior Product Manager":"270",
                       "Project Manager":"4","Senior Project Manager":"77","Data Engineer":"2732",
                       "Data Scientist":"25190","Senior Data Scientist":"25887","Machine Learning":"25206",
                       "Lead Data Scientist":"25885","Data Science Manager":"30009","Analytics Specialist":"30209",
                       "Data Associate":"7443","Business Intelligence Developer":"3282",
                        "Business Intelligence Analyst":"2336"}
            ### base url for job search
            url = 'https://www.linkedin.com/jobs/search/?f_JT=F'

            ### specific inputs
            period = job_period
            
            ### Applying the job titles filter
            if job_list:
                job_string = ''
                if job_list == 'Data Analyst':
                    for i in ["Data Analyst","Senior Data Analyst","Analytics Specialist","Data Associate"]:
                        job_string += '%2C' + job_title_dictionary[i]
                if job_list == 'Data Scientist':
                    for i in ["Data Scientist","Senior Data Scientist","Machine Learning","Lead Data Scientist","Data Science Manager"]:
                        job_string += '%2C' + job_title_dictionary[i]
                if job_list == 'Business Analyst':
                    for i in ["Business Analyst","Senior Business Analyst","Business Intelligence Analyst","Business Intelligence Developer"]:
                        job_string += '%2C' + job_title_dictionary[i]
                if job_list == 'Project Manager':
                    for i in ["Project Manager","Senior Project Manager"]:
                        job_string += '%2C' + job_title_dictionary[i]
                if job_list == 'Product Manager':
                    for i in ["Product Manager","Senior Product Manager"]:
                        job_string += '%2C' + job_title_dictionary[i]
                job_ids = '&f_T=' + job_string
                url+= job_ids 
            
            if keywords:
                keywords = '&keywords=' + urllib.parse.quote(keywords)
                url+= keywords
            
            if job_location:
                location = "&location=" + urllib.parse.quote(job_location)
            else:
                location = "&location=" + "United%20States"

            url += period + location

            if experience_level:
                if experience_level == "Entry":
                    exp = '&f_E=' + str(2)
                elif experience_level == "Associate":
                    exp = '&f_E=' + str(3)
                elif experience_level == "Mid-Senior":
                    exp = '&f_E=' + str(4)
                elif experience_level == "Director":
                    exp = '&f_E=' + str(5)
                url+= exp 

            # Filter on-site only
            if workplace_type:
                if workplace_type == 'On-site':
                    workplace_type = "&f_WT=1"
                elif workplace_type=="Remote":
                    workplace_type = "&f_WT=2"
                url+=workplace_type
            
            # To distinguish Washington state from Washington DC
            if geo_id:
                url = url + "&geoId={}".format(geo_id)
            elif job_location == "Washington":
                url = url + "&geoId=103977389"
            elif job_location == "San Francisco Bay Area":
                url = url + "&geoId=90000084"
            elif job_location == "Los Angeles Metropolitan Area":
                url = url + "&geoId=90000049"
            
            url = url
            
            return url
                
        except Exception as e:
            print("Error generating URL: ", e)
    
    def driver_launcher(self):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()
        time.sleep(5)
        return driver
    
    def extract_salary(self,text):
        pattern = r"(\$\d{1,3}(?:,\d{3})*(\.\d{2})?\s*-\s*\$\d{1,3}(?:,\d{3})*(\.\d{2})?)|(\$\d{1,3}(?:,\d{3})*(\.\d{2})?)"
        match = re.search(pattern, text)
        pattern_2 = r"\$\d+(?:,\d+)*(?:\.\d+)?\-\$\d+(?:,\d+)*(?:\.\d+)?"
        match_2 = re.search(pattern_2, text)
        if match_2:
            return match_2.group()
        elif match:
            return match.group() 
        else:
            return None
        
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
        if row['job_posted_age'] and not pd.isnull(row['job_posted_age']):
            match = re.search(r'\d+', row['job_posted_age'])
            number = int(match.group())
            if "day" in row['job_posted_age']:
                post_date = row['run_date'] - timedelta(days=number)
            elif "week" in row['job_posted_age']:
                post_date = row['run_date'] - timedelta(weeks=number)
            elif "hour" in row['job_posted_age']:
                post_date = row['run_date'] - timedelta(hours=number)
            elif "minute" in row['job_posted_age']:
                post_date = row['run_date'] - timedelta(minutes=number)
            elif "second" in row['job_posted_age']:
                post_date = row['run_date'] - timedelta(seconds=number)
            else:
                post_date = row['run_date']
        else:
            post_date = row['run_date']
        return post_date
    
    def extract_required_info(self,df_jobs):
        df_jobs['job_text'] = df_jobs['job_text'].fillna('')
        df_jobs['salary_range'] = df_jobs['job_text'].apply(self.extract_salary)
        df_jobs['experience'] = df_jobs['job_text'].apply(self.extract_years_of_experience)
        df_jobs['job_postdate'] =df_jobs.apply(lambda x: self.extract_post_date(x),axis=1)

        return df_jobs

    def extract_info(self,soup):
        job_dict = {}
        try:
            job_dict['job_title'] = soup.select("h2.topcard__title")[0].text
        except: 
            pass
        try:
            job_dict['job_company'] = soup.select("span.topcard__flavor")[0].find("a").text.strip()
        except: 
            pass
        try:
            job_dict['job_url']     = soup.select("a.topcard__link")[0].get("href")
        except: 
            pass
        try:
            job_dict['job_location'] = soup.select("span.topcard__flavor--bullet")[0].text.strip()
        except: 
            pass
        try:
            job_dict['job_seniority_level']=soup.select("span.description__job-criteria-text--criteria")[0].text.strip()
        except: 
            pass
        try:
            job_dict['job_emp_type'] = soup.select("span.description__job-criteria-text--criteria")[1].text.strip()
        except: 
            pass
        try:
            job_dict['job_function'] = soup.select("span.description__job-criteria-text--criteria")[2].text.strip()
        except: 
            pass
        try:
            job_dict['job_industry'] = soup.select("span.description__job-criteria-text--criteria")[3].text.strip()
        except: 
            pass
        try:
            job_dict['job_text']    = soup.select("div.show-more-less-html__markup")[0].text
        except: 
            pass
        try:
            job_dict['job_posted_age']=soup.select("span.topcard__flavor--metadata")[0].text.strip()
        except: 
            pass
        return job_dict
    
    def find_matching_skills(self,df, skills):
        results_df = pd.DataFrame(columns=['job_url', 'skill'])

        for index, row in df.iterrows():
            job_url = row['job_url']
            job_description = row['job_text']
            matching_skills = [skill for skill in skills if skill.lower() in job_description.lower()]
            job_results_df = pd.DataFrame({'job_url': [job_url]*len(matching_skills), 'skill': matching_skills})
            results_df = pd.concat([results_df, job_results_df], ignore_index=True)      
        return results_df

    
    def scrape_jobs(self,driver,url,job_role_input,job_location_input):
        driver.get(url)
        time.sleep(random.randint(5,10))
        count_jobs = 0
        while True:
            job_details_list = []
            total_page_elements = driver.find_elements(By.CLASS_NAME,'job-search-card')
            try:
                driver.find_element(By.CSS_SELECTOR,'button.infinite-scroller__show-more-button--visible').click()
                print("see_more_jobs_clicked")
                time.sleep(random.randint(5,10))
            except:
                pass
            for job_element in total_page_elements[count_jobs:]:
                job_element.click()
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                time.sleep(random.randint(5,10))
                job_dict = self.extract_info(soup)
                job_dict['job_role_input'] = job_role_input
                job_dict['job_role_location'] = job_location_input
                job_dict['run_date'] = datetime.now()
                job_details_list.append(job_dict)
            count_jobs+=len(job_details_list)
            df_jobs = pd.DataFrame(job_details_list)
            df_jobs.drop_duplicates(subset=['job_text','job_title','job_location'],inplace=True)
            df_jobs.to_sql(con=my_conn,name='linkedin_raw',if_exists='append',index=False)
            df_jobs_cleaned = self.extract_required_info(df_jobs)
            df_jobs.to_sql(con=my_conn,name='linkedin_cleaned',if_exists='append',index=False)
            df_skills = self.find_matching_skills(df_jobs,skills_list)
            df_skills.to_sql(con=my_conn,name='linkedin_skills',if_exists='append',index=False)

            #print(len(job_details_list))
            count_jobs_old = count_jobs
            if count_jobs == count_jobs_old:
                break

if __name__ == '__main__':
    job_list = ['Data Scientist','Data Analyst','Business Analyst']
    job_location = ["California","Texas","Virginia","New York","Washington","Florida","Illinois","Maryland",
                        "North Carolina","Massachusetts","Georgia","New Hampshire","Pennsylvania","Colorado",
                        "Ohio","Michigan"]
    
    for job_location_input in job_list:
        LinkedInJobScraper_class = LinkedInJobScraper()
        driver=LinkedInJobScraper_class.driver_launcher()
        for job_role_input in job_list:
            url=LinkedInJobScraper_class.url_gen( 
                                                job_list=job_role_input,
                                                job_location=job_location_input, 
                                                job_period="&f_TPR=r604800"
                                        )
            
            print(f'Process-Started for {job_role_input}-{job_location_input}')
            LinkedInJobScraper_class.scrape_jobs(driver,url,job_role_input,job_location_input)
            print(f'Process-Ended for {job_role_input}-{job_location_input}')
    driver.quit()