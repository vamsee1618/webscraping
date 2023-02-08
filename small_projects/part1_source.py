import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import time
from fake_useragent import UserAgent
import os
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
headers = {'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.56"}## Defining headers to avoid errors

def main():
    try:
        ### Part-1
        session_requests = requests.session()
        URL_LOGIN_PAGE = "https://www.planespotters.net/user/login/"
        page_login_request = session_requests.get(URL_LOGIN_PAGE,headers=headers)
        page_login_doc = BeautifulSoup(page_login_request.content, 'html.parser')
         
    
        cookies_login_page=session_requests.cookies.get_dict()
        print(cookies_login_page)
        
        csrf_input = page_login_doc.select("div.planespotters-form > form")[0].find("input", {"id": "csrf"}).get("value")

        print(csrf_input)
        print(type(csrf_input))
                      
        time.sleep(5) # 5s


        login_url = "https://www.planespotters.net/user/login/" #.format(rid_input)

        res_planespotter = session_requests.post(login_url, 
                                data = {
                                      
                                      "username" : "jornthebest", # your username here
                                      "password" : "jorn422", # your password here
                                      "csrf" : str(csrf_input),
                                      #"g-recaptcha-response":"",
                                      "rid":''
                                      },cookies=cookies_login_page,headers=headers,
                                
                                timeout = 15)
       
        cookies_post_login = session_requests.cookies.get_dict()
        print(cookies_post_login)

    
        time.sleep(5)
        # # #
        profile_page_url = "https://www.planespotters.net/member/profile"
        profile_page = session_requests.get(profile_page_url,  
                                      cookies=cookies_post_login,headers=headers)
        
        profiles_page_soup = BeautifulSoup(profile_page.content, 'html.parser')
        

        print(profiles_page_soup.text)
        if "jornthebest" in profiles_page_soup.text:
            print("Logged In Successfully")
        else:
            print("Log In Failed")
        
       
    except Exception as ex:
        print('error: ' + str(ex))

if __name__ == '__main__':
    main()

