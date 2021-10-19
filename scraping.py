import requests
from bs4 import BeautifulSoup

url = "http://books.toscrape.com/index.html"
#page = requests.get(url)  
#soup = BeautifulSoup(page.content, "html.parser")

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