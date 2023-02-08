from bs4 import BeautifulSoup
import requests
import time
import os
from tqdm import tqdm
import pandas as pd
import re
headers = {'User-Agent': 'Mozilla/5.0'} ## Defining headers to avoid errors

### Part-1
def download_ebay_page(page_num):
    try:
        url = "https://www.ebay.com/sch/i.html?LH_Sold=1&_nkw=amazon+gift+card"
        if page_num > 1:
            url+= '&_pgn={}'.format(str(page_num))
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        with open('html_pages/amazon_gift_card_{}.html'.format(str(page_num)), 'w', encoding="utf-8") as file:
            file.write(str(soup))
        time.sleep(10)
    except Exception as e:
        print(e)
        
def extract_salary(text):
        match = re.search(r'(\+\$\d+\.\d{2}|\$\d+)', text)
        if match:
            return match.group()
        else:
            return 0

def clean_dollars(text):
    try:
        replaced_text = re.sub(r'\$|\+\$', '', text)
        return float(replaced_text)
    except:
        return 0

for page_num in tqdm(range(1,11)):
    download_ebay_page(page_num)
print("pages successfully downloaded")

html_path = os.getcwd() + '\\html_pages\\'
master_data_list = []
for filename in os.listdir(html_path):
    if filename.endswith('.html') and "amazon" in filename:
        file_path = html_path + filename
        with open(file_path, 'r', encoding="utf-8") as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            required_data = soup.select("div.srp-river-results")[0].findAll("div",{"class":"s-item__info"})
            for item in required_data:
                data_dict={}
                data_dict['title']=item.find("div",{"class":"s-item__title"}).text
                data_dict['price']=item.find("span",{"class":"s-item__price"}).text
                try:
                    data_dict['shipping']=item.find("span",{"class":"s-item__logisticsCost"}).text
                except:
                    data_dict['shipping']="No Details"
                master_data_list.append(data_dict)
                
                
df_data=pd.DataFrame(master_data_list)
print(df_data)
df_data['price']=df_data['price'].apply(clean_dollars)
df_data['value']=df_data['title'].apply(extract_salary)
df_data['value']=df_data['value'].apply(clean_dollars)
df_data['shipping_costs']=df_data['shipping'].apply(extract_salary)
df_data['shipping_costs']=df_data['shipping_costs'].apply(clean_dollars)
df_data['total_cost']=df_data['shipping_costs'] + df_data['price']
df_data['value_ind']=df_data.apply(lambda row: 'below face value' if row['value'] >= row['total_cost'] else 'above face value',axis=1)
print(df_data[df_data['price']!=0]['value_ind'].value_counts())
sum(df_data['total_cost'] - df_data['value'])


#### Part-2
URL = "https://www.fctables.com/user/login/"

#An open session carries the cookies and allows you to make post requests
session_requests = requests.session()

res = session_requests.post(URL, 
                        data = 
                            {
                                "login_username": "jornthebest",
                                "login_password": "jorn422",
                                "user_remeber": 1,
                                "login_action": 1
                            },
                        timeout = 15)

cookies = session_requests.cookies.get_dict()

time.sleep(5)

url_bets = "https://www.fctables.com/tipster/my_bets/"
page_bets = session_requests.get(url_bets, cookies=cookies)
doc_bets = BeautifulSoup(page_bets.content, 'html.parser')

print(doc_bets.text);
print(cookies)
if "Wolfsburg" in doc_bets.text:
    print("Found WOlfsburg")
