from bs4 import BeautifulSoup
import requests
import json

URL = "https://www.lego.com/de-de"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}


categories = {}
list_of_found_products = []
SHOW_PRINTS = False

def get_category_sites():
    s = requests.Session()
    s.headers = headers
    source = s.get(URL, headers = headers).text
    soup = BeautifulSoup(source, "lxml")

    anchors = soup.find_all("a", class_ = "Linksstyles__Anchor-sc-684acv-0")
    for anchor in anchors:
        if "themes" not in anchor.get("href"):
            continue
        else:
            #print("https://www.lego.com" +anchor.get("href"))
            categories[anchor.text] = {"url" : "https://www.lego.com" +anchor.get("href"), "category" :  anchor.get("href").split("/")[-1].replace("-", " ").title()}
    
   # print(categories)
    # for key in categories:
    #     print(key, " >> ", categories[key])
    #     print("______________________")
      
def get_site_pages(url):
    s = requests.Session()
    s.headers = headers
    source = s.get(url, headers = headers).text
    soup = BeautifulSoup(source, "lxml")

    max_products = 0
    product_amount = soup.find_all("span", class_ = "Text__BaseText-sc-13i1y3k-0")
    for span in product_amount:
        if span.get("data-test") == "result-count":
            max_products = int(span.get("data-value"))
            break

    pages = max_products // 18
    if max_products % 18 != 0:
        pages += 1

    return pages


def get_products_from_site(url, category):

    if SHOW_PRINTS:
        print("#####################################################################")
        print("Get product infos for", category)
    pages = get_site_pages(url)

    if pages == None:
        return


    for i in range(1, pages+1):
        if SHOW_PRINTS:
            print(f"_______________page {i}_______________________")
        url_to_scrape = f"{url}?page={i}"
        if SHOW_PRINTS:
            print(url_to_scrape)

        try:
            s = requests.Session()
            s.headers = headers
            source = s.get(url_to_scrape, headers = headers).text
            soup = BeautifulSoup(source, "lxml")

            product_wrappers = soup.find_all("li", class_ = "Grid_grid-item__FLJlN")


            for product_wrapper in product_wrappers:
                if product_wrapper.get("data-test") != "product-item":
                    continue

                # name, id and link
                possible_titles = product_wrapper.find_all("a", class_="body-md-medium")

                for possible_title in possible_titles:
                    if possible_title.get("data-test") == "product-leaf-title":
                        try:
                                title = possible_title.text
                                original_link = "https://www.lego.com" +possible_title.get("href")
                                id = original_link.split("-")[-1]
                                break
                        except:
                            continue
                if id == None:
                    continue

                #price
                price = product_wrapper.find("span", class_ ="price-sm-bold")
                if price != None:
                    price = price.text.replace("€", "").replace(",", ".")
                else:
                    continue

                # baseprice
                pieces = 0
                possible_baseprices = product_wrapper.find_all("span", class_= "label-sm-medium")
                for possible_baseprice in possible_baseprices:
                    if possible_baseprice.get("data-test") == "product-leaf-piece-count-label":
                        pieces = possible_baseprice.text
                        break
                
                if pieces == 0:
                    baseprice = price
                    unit = "€ pro Artikel"
                else:
                    baseprice = round(float(price) / float(pieces), 2)
                    unit = "€ pro Legostein"


                new_dict = {
                "id" : id,
                "unit" : unit,
                "price" : price, 
                "baseprice" : baseprice,
                "category" : category,
                "imageURL" : "#",
                "original_link" : original_link,
                "name" : title
                }

                if new_dict not in list_of_found_products:
                        if SHOW_PRINTS:
                            print(id, title, category)
                        list_of_found_products.append(new_dict)
        except Exception as e:
            print("error getting page products", e)
    
    

def get_products_from_shop():
    current = 1
    get_category_sites()
    for category_site in categories:
        print(current, "of", len(categories))
        current += 1
        if "?" in categories[category_site]["url"]:
            continue

        get_products_from_site(categories[category_site]["url"], categories[category_site]["category"])
    
    return list_of_found_products


