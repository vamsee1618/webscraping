import pymongo
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from urllib.parse import quote
client = pymongo.MongoClient("mongodb://localhost:27017/")

### Question-1
### Selenium
def q1_selenium():
    try:
        url_1 = "https://opensea.io/collection/boredapeyachtclub?search[sortAscending]=false&search[stringTraits][0][name]=Fur&search[stringTraits][0][values][0]=Solid%20Gold"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        time.sleep(5)

        driver.get(url_1)
        time.sleep(10)

        main_html = driver.page_source
        main_soup = BeautifulSoup(main_html, 'html.parser')
        bayc_each_list = []
        for bayc_link in main_soup.find_all("a",{"class":"Asset--anchor"})[:8]:
            bayc_each_list.append(bayc_link.get("href"))

        for bayc in tqdm(bayc_each_list):
            driver.find_element(By.XPATH,"//a[@href='{}']".format(bayc)).click()
            time.sleep(20)
            each_html = driver.page_source
            each_soup = BeautifulSoup(each_html, 'html.parser')
            with open('bayc_{}.html'.format(bayc.split('/')[-1]), 'w', encoding="utf-8") as file:
                file.write(str(each_soup))
            driver.back()
            time.sleep(20)
        print("All the BAYC NFTs successfully downloaded")
    except Exception as e:
        print(e)
    

### Question-2
### BAYC Mangodb 
def q2_mangodb():
    try:
        proj_db = client["ind_proj"]
        bayc_collection = proj_db["bayc"]
        
        for entry in os.scandir('.'):
            if entry.name.endswith(".html"):
                with open(entry.name, 'r', encoding="utf-8") as file:
                    html_content = file.read()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    soup.find("h1", {"class": "item--title"}).text[1:]
                    bayc_ind_dict={}
                    bayc_ind_dict['ape_name']=soup.find("h1", {"class": "item--title"}).text[1:]
                    bayc_prop_list = []
                    
                    for i in soup.find_all("div",{"class":"item--property"}):
                        bayc_prop_dict={}
                        bayc_prop_dict['property_type']=i.find("div",{"class":"Property--type"}).text
                        bayc_prop_dict['property_value']=i.find("div",{"class":"Property--value"}).text
                        bayc_prop_dict['property_rarity']=i.find("div",{"class":"Property--rarity"}).text
                        bayc_prop_list.append(bayc_prop_dict)
                    properties_dict = {}
                    
                    for prop in bayc_prop_list:
                        prop_type = prop["property_type"]
                        prop_value = prop["property_value"]
                        prop_rarity = prop["property_rarity"]   
                        properties_dict[prop_type] = {}
                        properties_dict[prop_type]['property_value'] = prop_value
                        properties_dict[prop_type]['property_rarity'] = prop_rarity
                    
                    bayc_ind_dict['attributes']=properties_dict
                    bayc_collection.insert_one(bayc_ind_dict)
                    print("Successfully Sent {}".format(entry.name))
    except Exception as e:
        print(e)    

def q3_req():
    try:
        base_url = "https://www.yellowpages.com/search?search_terms=Pizzeria&geo_location_terms=San+Francisco%2C+CA"
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        with open('sf_pizzeria_search_page.html', 'w', encoding="utf-8") as file:
            file.write(str(soup))
        print("Pizzeria Page Successfully Downloaded")
    except Exception as e:
        print(e)

def q4_print_pizzeria():
    try:
        with open('sf_pizzeria_search_page.html', 'r', encoding="utf-8") as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            search_results = soup.find_all('div', {'class': 'search-results organic'})[0].find_all('div',{'class':'result'})
        for result in search_results:
            pizzeria_dict = {}
            pizzeria_dict['rank'] = result.find('h2', {'class': 'n'}).text.split(' ',1)[0][:-1]
            pizzeria_dict['name'] = result.find('h2', {'class': 'n'}).text.split(' ',1)[1]
            pizzeria_dict['link'] = result.find('a', {'class': 'business-name'}).get('href')
            try:
                rating = result.find('a', {'class': 'rating'})
                pizzeria_dict['stars'] = rating.find('div',{'class':'result-rating'}).attrs['class'][1]
                pizzeria_dict['num_reviews'] = rating.find('span', {'class': 'count'}).text.strip('()')
            except:
                pass
            try:
                tripadvisor_rating = result.find('div', {'class': 'ratings'})
                pizzeria_dict['tripadv_stars'] = eval(tripadvisor_rating.get("data-tripadvisor"))['rating']
                pizzeria_dict['tripadv_reviews'] = eval(tripadvisor_rating.get("data-tripadvisor"))['count']
            except:
                pass
            try:
                pizzeria_dict['dollar_sign'] = len(result.find('div', {'class': 'price-range'}).text)
            except:
                pass
            try:
                pizzeria_dict['years_in_business'] = result.find('div', {'class': 'number'}).text.strip()
            except:
                pass
            try:
                pizzeria_dict['review'] = result.find('div', {'class': 'snippet'}).text.strip()
            except:
                pass
            try:
                amentities_list = [i.text for i in result.find('div', {'class': 'amenities-info'})]
                pizzeria_dict['amentities'] = amentities_list
            except:
                pass
            
            print(pizzeria_dict)
    except Exception as e:
        print(e)

def q5_pizzeria_mangodb():
    try:
        proj_db = client["ind_proj"]
        pizzeria_collection = proj_db["sf_pizzerias"] 
        with open('sf_pizzeria_search_page.html', 'r', encoding="utf-8") as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            search_results = soup.find_all('div', {'class': 'search-results organic'})[0].find_all('div',{'class':'result'})
        for result in tqdm(search_results):
            pizzeria_dict = {}
            pizzeria_dict['rank'] = result.find('h2', {'class': 'n'}).text.split(' ',1)[0][:-1]
            pizzeria_dict['name'] = result.find('h2', {'class': 'n'}).text.split(' ',1)[1]
            pizzeria_dict['link'] = result.find('a', {'class': 'business-name'}).get('href')
            try:
                rating = result.find('a', {'class': 'rating'})
                pizzeria_dict['stars'] = rating.find('div',{'class':'result-rating'}).attrs['class'][1]
                pizzeria_dict['num_reviews'] = rating.find('span', {'class': 'count'}).text.strip('()')
            except:
                pass
            try:
                tripadvisor_rating = result.find('div', {'class': 'ratings'})
                pizzeria_dict['tripadv_stars'] = eval(tripadvisor_rating.get("data-tripadvisor"))['rating']
                pizzeria_dict['tripadv_reviews'] = eval(tripadvisor_rating.get("data-tripadvisor"))['count']
            except:
                pass
            try:
                pizzeria_dict['dollar_sign'] = len(result.find('div', {'class': 'price-range'}).text)
            except:
                pass
            try:
                pizzeria_dict['years_in_business'] = result.find('div', {'class': 'number'}).text.strip()
            except:
                pass
            try:
                pizzeria_dict['review'] = result.find('div', {'class': 'snippet'}).text.strip()
            except:
                pass
            try:
                amentities_list = [i.text for i in result.find('div', {'class': 'amenities-info'})]
                pizzeria_dict['amentities'] = amentities_list
            except:
                pass
            
            pizzeria_collection.insert_one(pizzeria_dict)
    except Exception as e:
        print(e)        

def q6_pizzeria_download_page():
    try:
        base_url = "https://www.yellowpages.com"
        proj_db = client["ind_proj"]
        pizzeria_collection = proj_db["sf_pizzerias"]

        for doc in tqdm(pizzeria_collection.find()):
            rank = doc['rank']
            url = base_url+doc['link']
            response = requests.get(url)
            time.sleep(10)
            soup = BeautifulSoup(response.content, 'html.parser')
            with open('sf_pizzerias_{}.html'.format(rank), 'w', encoding="utf-8") as file:
                file.write(str(soup))
            time.sleep(5)
    except Exception as e:
        print(e)

def q7_pizzeria_address():
    try:
        pizzeria_list = []
        for i in range(1,31):
            with open('sf_pizzerias_{}.html'.format(i), 'r', encoding="utf-8") as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')
            pizz_dict = {}
            pizz_dict['address']=soup.find('span',{"class":"address"}).text
            pizz_dict['phone_number']=soup.find('a',{'class':'phone'}).get("href")[4:]
            try:
                pizz_dict['website']=soup.find_all('a',{'class':'dockable'})[1].get("href")
            except:
                pass
            pizzeria_list.append(pizz_dict)
        print(pizzeria_list)
    except Exception as e:
        print(e) 

def q8_api_key():
    try:
        base_url = "http://api.positionstack.com/v1/forward?access_key=&query="
        pizzeria_list = []
        for i in range(1,31):
            with open('sf_pizzerias_{}.html'.format(i), 'r', encoding="utf-8") as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')
            pizz_dict = {}
            pizz_dict['address']=soup.find('span',{"class":"address"}).text
            pizz_dict['phone_number']=soup.find('a',{'class':'phone'}).get("href")[4:]
            pizz_dict['website']=soup.find_all('a',{'class':'dockable'})[1].get("href")
            pizzeria_list.append(pizz_dict)

        geo_pizzeria_list=[]
        for pizz_dict in tqdm(pizzeria_list):
            address_space = pizz_dict['address'].find("San Francisco") 
            new_address = pizz_dict['address'][:address_space] + " " + pizz_dict['address'][address_space:]
            url_gen = base_url + quote(new_address)
            for i in range(10):
                try:
                    geo_dict=requests.get(url_gen).json()['data'][0]
                    lat = geo_dict['latitude']
                    long = geo_dict['longitude']
                    pizz_dict['address']=new_address
                    pizz_dict['geo_location']= {'latitude': lat, 'longitude': long}
                    geo_pizzeria_list.append(pizz_dict)
                    time.sleep(10)
                    break
                except:
                    continue
                    time.sleep(5)
        
        proj_db = client["ind_proj"]
        pizzeria_collection = proj_db["sf_pizzerias"]

        for doc,add in zip(pizzeria_collection.find(),geo_pizzeria_list):
            update = {"$set": add}
            pizzeria_collection.update_one({"rank": doc["rank"]}, update)
    
    except Exception as e:
        print(e)

        

if __name__ == "__main__":
    q1_selenium()
    q2_mangodb()
    q3_req()
    q4_print_pizzeria()
    q5_pizzeria_mangodb()
    q6_pizzeria_download_page()
    q7_pizzeria_address()
    q8_api_key()