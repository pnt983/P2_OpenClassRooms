import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from posixpath import basename
import re
from pathlib import Path
import csv


def get_and_parse_url(url):
    page_response = requests.get(url)
    if not page_response.ok:
        print("Oups! Un probleme est apparue lors de la requete au serveur")
        return
    soup = BeautifulSoup(page_response.content, "html.parser")
    return soup


def get_category_name_for_csv(url):
    """Recupere le nom de la categorie pour pouvoir creer le csv"""
    soup = get_and_parse_url(url)

    category = soup.find('ul', class_='breadcrumb')
    find_li = category.find_all('li')
    name_file = find_li[2].text.strip()
    return name_file


def save_data_book_csv(dict_name, categorie_name):
    """ Enregistre les donnees des livres par page"""
    fieldname = dict.keys(dict_name)
    file_path = Path("Data/"+categorie_name+ "/"+categorie_name+".csv")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open('a', encoding="utf-8-sig") as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=fieldname, delimiter=",")
        if file_csv.tell() == 0:
            writer.writeheader()
        writer.writerow(dict_name)


def save_image(title, list_url, categories):
    """ Enregistre l'image du livre"""
    clean_title = re.sub(r"[^a-zA-Z0-9]", "_", title)
    file_path = Path("Data/"+categories+"/"+clean_title+".jpg")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open('wb') as image_jpg:
        response = requests.get(list_url)
        image_jpg.write(response.content)
        image_jpg.close()


def get_book_data(url):
    """ Enregistre toutes les donnees d'un livre dans un csv"""
    soup = get_and_parse_url(url)

    tds = soup.find_all('td')
    description = soup.find_all('p')
    product_description = description[3].text
    categories = soup.find_all('li')
    category = categories[2].text.strip()
    title = (soup.find('h1')).text
    dict_rating = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    get_rating = soup.find("p", class_=re.compile("star-rating")).get("class")[1]
    get_rating = dict_rating[get_rating]
    get_image = soup.find('div', class_='item active')
    source_image = get_image.find('img')
    url_image = source_image.get('src')
    url_image = url_image.replace("../", "")
    parse_url = urlparse(url)
    parse_object = parse_url
    url_base = basename(parse_object.netloc)
    list_url = ("https://"+url_base + '/' + url_image)
    clean_title = re.sub(r"[^a-zA-Z0-9]", "_", title)
    file_path = Path("P2_Despierre_Clement/"+category+"/"+clean_title+".jpg")
    dictionnary_book_description = {}
    save_image(title, list_url, category)             
    universal_product_code = tds[0].text
    price_including_tax = tds[3].text
    price_excluding_tax = tds[2].text
    number_available = tds[5].text
    number_available = re.sub(r'[^0-9]', '', number_available)
    dictionnary_book_description = {
        'Title': title,
        'UPC': universal_product_code,
        'price_including_tax': price_including_tax,
        'price_excluding_tax': price_excluding_tax,
        'number_available': number_available,
        'Description': product_description,
        'Categorie': category,
        'review-rating': get_rating,
        'url_image': list_url,
        'local_image': file_path,
        'url_page': url}
    print(f"Les donnees du livre {title} sont recuperees")
    return dictionnary_book_description


def get_categories_url(url):
    """Recupere l'url de toutes les categories sur la page d'accueil"""
    soup = get_and_parse_url(url)

    category_list = []
    get_ul = soup.find('ul', class_='nav nav-list')
    all_li = get_ul.find_all('a')
    for get_href in all_li:
        get_href = get_href['href']
        parse_url = urlparse(url)
        url_base = basename(parse_url.netloc)
        final_url = url_base.replace(url_base, get_href)
        category_list.append("https://" + url_base + '/' + final_url)
    category_list.remove(category_list[0])
    print("Recuperation de l'url de chaque categorie fini")
    return category_list


def get_book_by_page(url):
    """ Recupere toutes les urls des livres sur une page """
    soup = get_and_parse_url(url)

    url_book_list = []
    get_div = soup.find_all('article', class_="product_pod")
    for get_href in get_div:
        href = get_href.div.a.get('href')
        replace_href_url = href.replace("../", "")
        parse_url = urlparse(url)
        url_base = basename(parse_url.netloc)
        url_book_list.append("https://" + url_base + "/" + "catalogue" + "/" + replace_href_url)
    print(f"La recuperation de l'url du livre {replace_href_url} est fini")
    return url_book_list


def get_loop(url):
    soup = get_and_parse_url(url)

    get_book_numbers = soup.find("form", class_="form-horizontal")
    numbers = get_book_numbers.find_all("strong")
    number = numbers[0].text.strip()
    division = int(number) // 20
    modulo = int(number) % 20
    if modulo != 0:
        division += 1
        return division
    else:
        return division


def main():
    URL = "http://books.toscrape.com/index.html"

    categories_url = get_categories_url(URL)
    books_urls = []
    for categorie_url in categories_url:
        loops = get_loop(categorie_url)
        for loop in range(loops):
            if loop > 0:
                page_number = loop + 1  # range commence à zero
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
