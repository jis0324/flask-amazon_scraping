
import requests
import re
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from lxml.html import fromstring
from itertools import cycle
import traceback
import pymongo
import argparse
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
ua=UserAgent()
#mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")
mongoclient = pymongo.MongoClient("mongodb+srv://Mycle:Piterpiter@cluster0-dqqoe.mongodb.net/test?retryWrites=true&w=majority")
db = mongoclient["amazon_data"]

# def get_proxies():
#     url = 'https://free-proxy-list.net/'
#     response = requests.get(url)
#     parser = fromstring(response.text)
#     proxies = set()
#     for i in parser.xpath('//tbody/tr')[:400]:
#         if i.xpath('.//td[7][contains(text(),"yes")]'):
#             proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
#             print(proxy)
#             proxies.add(proxy)
#     return proxies

def get_proxies():
    with open('proxy.txt') as f:
        proxylist = f.read().splitlines()
        #print(proxylist[:3])
    return proxylist


proxies = get_proxies()
#print(len(proxies))
proxy_pool = cycle(proxies)
# print(next(proxy_pool))
def get_converted_price(price):
    #print("######",price)
    converted_price = float(re.sub(r"[^\d.]", "", price.split('-')[0]))
    return converted_price


def extract_url(url):

    if url.find("www.amazon.com") != -1:
        index = url.find("/dp/")
        print(index,'gp')
        if index != -1:
            index2 = index + 14
            url = "https://www.amazon.com" + url[index:index2]
        else:
            index = url.find("/gp/")
            print(index,'gp')
            if index != -1:
                index2 = index + 22
                url = "https://www.amazon.com" + url[index:index2]
            else:
                url = None
    else:
        url = None
    return url


def get_product_details(url):
    

    
    details = {"name": "", "price": 0, "deal": True, "url": ""}
    price = None
    title = None
    headers = {'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
            }
    _url = extract_url(url)
    print("logging: URL = %s"%_url)
    if _url is None:
        details = None
    else:
        try:
            response = requests.get(_url, headers=headers)
            soup = BeautifulSoup(response.content, "html5lib")
            price = price = soup.find(id="priceblock_dealprice") or soup.find(id='priceblock_saleprice')
            title = soup.find(id="productTitle")
            if price is None:
                price = soup.find(id='color_name_0_price')
                details["deal"] = False    
            if price is None:
                price = soup.find(id="priceblock_ourprice")
                # print (price)
                details["deal"] = False
        except Exception as e:
            print(e)
            if price is None or title is None:
                for i in range(1):
                    # proxy = next(proxy_pool)
                    proxy = random.choice(proxies)
                    print(proxy)
                    try:
                        response = requests.get(_url, headers=headers, proxies={"http": proxy, "https": proxy}, timeout=15)
                        soup = BeautifulSoup(response.content, "html5lib")
                        title = soup.find(id="productTitle")
                        price = soup.find(id="priceblock_dealprice") or soup.find(id='priceblock_saleprice')
                        if price is None:
                            price = soup.find(id='color_name_0_price')
                            details["deal"] = False    
                        if price is None:
                            price = soup.find(id="priceblock_ourprice")
                            # print (price)
                            details["deal"] = False 
                        print(price , title)
                        if price is not None or title is not None:
                            break
                        
                    except Exception as e:
                        print("Skipping attempt %s. Connnection error %s"%(i,e))
        
        if title is not None and price is not None:
            details["name"] = title.get_text().strip()
            details["price"] = price.get_text()#get_converted_price(price.get_text())
            details["url"] = _url
        elif title is not None and price is None:
            details["name"] = title.get_text().strip()
            details["price"] = "No Price"
            details["url"] = _url
        else:
            details = None
    return details

def save_to_mongo(document):
    '''
    Saves or Updates Mongo db
    document : type: Dictionary

    '''
    collection = db['scrapped_data']
    data = collection.find_one({'url':document.get('url')})
    if data:
        print("Already existing data, Updating")
        data['name'] = document.get('name')
        data['price'] = document.get('price')
        data['deal'] = document.get('deal')
        # print(dir(data))
        data.update()
    else:
        data = collection.insert_one(document)
    return data

def main_scrapper(product_url):
# if __name__ == '__main__':
    #product_url = "https://www.amazon.com/Vivii-velas-llama-velas-falsas-bater%C3%ADa/dp/B01MQ1Q3R1?pf_rd_r=CTEWXXM0ZRPGERP822HK&pf_rd_p=277a7e11-1bef-478c-bd76-67176c3b2794&pd_rd_r=6da7826a-b855-499d-b424-230e25bc6416&pd_rd_w=PZTfw&pd_rd_wg=Vi9dp&ref_=pd_gw_unk"
    # parser = argparse.ArgumentParser(
    #     description='Simple scraper to extract all products from Amazon')
    # parser.add_argument('--url', '-u' , default='',help='URL of the Amazon site')
    # args = parser.parse_args()
    # product_url = args.url
    data = get_product_details(product_url)
    flagged_data = save_to_mongo(data)
    # print(data)
    return data