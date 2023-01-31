import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import time
import os
headers = {'User-Agent': 'Mozilla/5.0'} ## Defining headers to avoid errors

## Function to get URLs
def get_url_barnes(page_num,books_per_page):
    """
    Input Parameters:
        page_num       : page to view
        books_per_page : no of books per page
    Output
        URL 
    """
    base_barnes_url = "https://www.barnesandnoble.com/b/books/_/N-1fZ29Z8q8?"
    final_url = base_barnes_url + 'Nrpp={}&page={}'.format(str(books_per_page),str(page_num))
    return final_url

barnes_nobble = requests.get(get_url_barnes(1,40),headers=headers)
## Check for page load status
if barnes_nobble.status_code == 200:
    barnes_nobble_soup = BeautifulSoup(barnes_nobble.text, 'lxml')

## Collect all the URLs
books_urls = []
base_url = 'https://www.barnesandnoble.com/'
for i in range(40):
    book = barnes_nobble_soup.findAll("div",{"class":"product-shelf-title"})[i].find('a').get('href')
    books_urls.append(base_url + book)

print(len(books_urls))

## Download htmls for every 5 seconds
for i in tqdm(range(len(books_urls))):
    response = requests.get(books_urls[i],headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    with open('html_pages/bn_top100_{}.html'.format(str(i)), 'w', encoding="utf-8") as file:
        file.write(str(soup))
    time.sleep(5)

## Load HTML and print the first 100 characters
html_path = os.getcwd() + '\\html_pages\\'
for filename in os.listdir(html_path):
    if filename.endswith('.html'):
        file_path = html_path + filename
        with open(file_path, 'r', encoding="utf-8") as file:
            html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            print(soup.findAll("div",{"class":"bs-content"})[0].text[:100])