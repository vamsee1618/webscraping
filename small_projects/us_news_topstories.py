### Importing required libraries
import requests
from bs4 import BeautifulSoup
import re
headers = {'User-Agent': 'Mozilla/5.0'} ## Defining headers to avoid errors


def main():
    try:
        ##Part-1
        price_dict = {} ## Dictionary to capture the results
        url = 'https://www.tigerdirect.com/applications/SearchTools/item-details.asp?EdpNo=1501390'
        ##Load the page
        hp_omen_request = requests.get(url,headers=headers)
        ## Check for page load status
        if hp_omen_request.status_code == 200:
            hp_omen_soup = BeautifulSoup(hp_omen_request.text, 'lxml')
            current_price_dollar = hp_omen_soup.select("div.col-sm-12.col-lg-5.pdp-specs-info > div > div.pdp-price > p:nth-child(3) > span.sale-price")[0].text ##Find current price
            current_price= re.findall(r'\$(.*?)\$', current_price_dollar, re.DOTALL) ## Clean the price
            price_dict['current_price'] = float(re.sub(r',', '', current_price[0]))
            list_price_dollar = hp_omen_soup.select("div.col-sm-12.col-lg-5.pdp-specs-info > div > div.pdp-price > p.list-price > span:nth-child(3) > del")[0].text
            list_price_dollar=re.sub(r"\$", "", list_price_dollar)
            price_dict['list_price'] = float(re.sub(r',', '', list_price_dollar))
            print(price_dict)
        else:
            print("The page didn't load properly")
        ##Part-2
        us_news_url = "https://www.usnews.com/"
        us_news_request = requests.get(us_news_url,headers=headers)
        if us_news_request.status_code == 200:
            us_news = {}
            us_news_soup = BeautifulSoup(us_news_request.text, 'lxml')
            productDivs = us_news_soup.findAll('div', attrs={'class' : "Box-w0dun1-0 ArmRestTopStories__Part-s0vo7p-1 erkdnc biVKSR"})
            for div in productDivs:
                url_list = div.findAll('a')
            us_news['second_url'] = url_list[3].get('href')
            print(us_news)
            url_second_top_page = BeautifulSoup(requests.get(us_news['second_url'],headers=headers).text, 'lxml')
            us_news['second_url_header'] = url_second_top_page.select("#app > div.Box-w0dun1-0.dWWnRo > div.Content-sc-837ada-0.kkKJUL.content > div.Box-w0dun1-0.kLgpNr.villain-article__CustomVillain-zujirt-0.kgNsfr.article__VillainArticle-sc-1ng6nv6-6.itHiSy.villain-article__CustomVillain-zujirt-0.kgNsfr.article__VillainArticle-sc-1ng6nv6-6.itHiSy > div.Villain__FlexDiv-sc-1y12ps5-0.ibtdoQ > div > div > div.Villain__TitleContainer-sc-1y12ps5-6.knjdTo > h1")[0].text
            sentences=re.match(r"(.*?[.!?]){1,3}",url_second_top_page.select("#ad-in-text-target")[0].text)
            us_news['text']= sentences.group(0)
            print(us_news)
        else:
            print("The page didn't load properly")
    except Exception as e:
        print("Problem with the connection")
        print(e)
        
if __name__ == '__main__':
    main()