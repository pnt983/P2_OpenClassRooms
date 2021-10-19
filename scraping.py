import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from posixpath import basename
import re
import csv

url = "http://books.toscrape.com/index.html"


def get_book_data(url):
    """ Enregistre toutes les donnees d'un livre dans un csv"""
    page = requests.get(url)  
    soup = BeautifulSoup(page.content, "html.parser")

    tds = soup.find_all('td')
    description = soup.find_all('p')         
    product_description = description[3].text
    category = soup.find_all('li')
    categories = category[2].text.strip()
    title = (soup.find('h1')).text
    dict = {'One':1,'Two':2,'Three':3,'Four':4,'Five': 5}
    rating_list = []
    get_rating = soup.find("p", class_ = re.compile("star-rating")).get("class")[1]
    get_rating = dict[get_rating]
    rating_list.append(get_rating)
    list_url = []
    image = soup.find('div',class_='item active')
    source_image = image.find('img')
    url_image = source_image.get('src')
    url_image = url_image.replace("../","")
    parse_url = urlparse(url)
    parse_object = parse_url
    url_base = basename(parse_object.netloc)
    list_url.append(url_base + '/' + url_image)
    dictionnary_book_description= {}
    for td in tds:
        universal_product_code = tds[0].text
        price_including_tax = tds[3].text
        price_excluding_tax = tds[2].text
        number_available = tds[5].text
        number_available = re.sub(r'[^0-9]', '', number_available)  
        dictionnary_book_description= {
            'UPC': universal_product_code,
            'price_including_tax' : price_including_tax,
            'price_excluding_tax' : price_excluding_tax,
            'number_available' :number_available,
            'Description': product_description,
            'Categorie':categories,
            'Title':title,
            'review-rating' : rating_list,
            'url_image' : list_url,
            'url_page' : url}
    return dictionnary_book_description


def get_categories_url(url):
    """Recupere l'url de toutes les categories sur la page d'accueil"""
    page = requests.get(url)  
    soup = BeautifulSoup(page.content, "html.parser")
   
    get_ul = soup.find('ul', class_='nav nav-list')
    category_list = []
    all_li = get_ul.find_all('a')
    for get_href in all_li :
        get_href = get_href ['href']
        parse_url = urlparse(url)
        url_base = basename(parse_url.netloc)
        final_url = url_base.replace(url_base,get_href)
        category_list.append("https://"+url_base + '/' +final_url)
    category_list.remove(category_list[0])
    return category_list

def get_book_by_page(url):
    """ Recupere toutes les urls des livres sur une page """
    page = requests.get(url)  
    soup = BeautifulSoup(page.content, "html.parser")

    url_book_list = []
    get_div = soup.find_all('article', class_="product_pod")
    for get_href in get_div:
        href = get_href.div.a.get('href')
        replace_href_url= href.replace("../","")
        parse_url = urlparse(url)
        url_base = basename(parse_url.netloc)
        url_book_list.append("https://" + url_base +"/"+"catalogue"+"/"+ replace_href_url) 
    return url_book_list

def button_next_page(url):
    """Regarde si il a une autre page. Si il y en a une autre, recuperation de l'adresse de l'autre page"""
    page = requests.get(url)  
    soup = BeautifulSoup(page.content, "html.parser")
    
    next_page= soup.find('li', class_='next')
    while soup.find('li', class_='next') is not None:
        next_page_url=next_page.find('a')
        find_href= next_page_url.get('href')
        parse_url = urlparse(url)
        parse_object = parse_url
        url_base = basename(parse_object.path)
        final_url = url.replace(url_base, find_href)
        return (final_url)

def get_category_name_for_csv(url): 
    """Recupere le nom de la categorie pour pouvoir creer le csv"""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    category = soup.find('ul', class_='breadcrumb')
    find_li = category.find_all('li')
    name_file= find_li[2].text.strip()
    return name_file

def save_data_book_csv(dict_name, categorie_name):
    """ Enregistre les donnees des livres par page"""
    fieldname = dict.keys(dict_name)
    with open(categorie_name +'.csv','a') as file_csv:          
        writer = csv.DictWriter (file_csv,fieldnames=fieldname, delimiter = ",")
        if file_csv.tell()==0 :
            writer.writeheader()
        writer.writerow(dict_name)