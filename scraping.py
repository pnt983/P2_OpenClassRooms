import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from posixpath import basename
import re
from pathlib import Path
import csv


url = "http://books.toscrape.com/index.html"


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
    file_path = Path ("P2_Despierre_Clement/data_csv/"+categorie_name+".csv")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open('a',encoding="utf-8-sig") as file_csv:   
        writer = csv.DictWriter (file_csv,fieldnames=fieldname, delimiter = ",")
        if file_csv.tell()==0 :
            writer.writeheader()
        writer.writerow(dict_name)

def save_image (title,url) :
    """ Enregistre l'image du livre"""
    clean_title = re.sub(r"[^a-zA-Z0-9]","_",title)
    file_path = Path ("P2_Despierre_Clement/books_images/"+clean_title+".jpg")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open('wb') as image_jpg :   
        response = requests.get(url)
        image_jpg.write(response.content)
        image_jpg.close()   
         
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
    dict_rating = {'One':1,'Two':2,'Three':3,'Four':4,'Five': 5}
    get_rating = soup.find("p", class_ = re.compile("star-rating")).get("class")[1]
    get_rating = dict_rating[get_rating]
    image = soup.find('div',class_='item active')
    source_image = image.find('img')
    url_image = source_image.get('src')
    url_image = url_image.replace("../","")
    parse_url = urlparse(url)
    parse_object = parse_url
    url_base = basename(parse_object.netloc)
    list_url = (url_base + '/' + url_image)    
    dictionnary_book_description= {}
    save_image(title,url)                            
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
            'review-rating' : get_rating,
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

def get_loop(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    get_book_numbers = soup.find("form", class_="form-horizontal")
    numbers = get_book_numbers.find_all("strong")
    number= numbers[0].text.strip()
    division = int(number) // 20
    modulo = int(number) % 20
    if modulo != 0:
        division += 1
        return division
    else:
        return division

def main():
    page_response = requests.get(url)
    soup = BeautifulSoup(page_response.content, "html.parser")

    categories_url = get_categories_url(url)
    print(categories_url)
    books_urls = []  
    for categorie_url in categories_url:
        loops = get_loop(categorie_url)
        for loop in range (loops):
            if loop > 0:
                page_number = loop + 1 # range commence à zero
                current_url = categorie_url.replace("index.html", f"page-{page_number}.html")
                book_on_next_page = get_book_by_page(current_url)
                books_urls.extend(book_on_next_page) 
            else:
                book_by_page = get_book_by_page(categorie_url)
                books_urls.extend(book_by_page)
                loop += 1
    
    
    for book_url in books_urls:
        book_data = get_book_data(book_url)
        categorie_name = get_category_name_for_csv(book_url)
        save_data_book_csv(book_data, categorie_name)
            
    
if __name__ == "__main__":
    main()
        