from bs4 import BeautifulSoup
import requests
URL = "https://www.medikamente-per-klick.de/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}

SHOW_PRINTS = True
categories = []
found_products = []

def get_categories():
    global categories
    print("Get Categories")
    url = "https://www.medikamente-per-klick.de/"
    s = requests.Session()
    s.headers = headers
    source = s.get(url, headers = headers).text
    soup = BeautifulSoup(source, "lxml")


    main_category_wrappers = soup.find_all("li", class_= "submenu01")
    current = 0

    for main_category in main_category_wrappers:

        
        # with open("testi.html", "w", encoding="UTF-8") as file:
        #     file.write(main_category.prettify())
        # print("save in testi.html")
      
        main_category_name = main_category.text.strip()
        main_category_url = main_category.find("a").get("href")

        if main_category_name.lower().strip() == "wir empfehlen":
            continue
        
        current += 1
        if SHOW_PRINTS:
            print(current, "of", len(main_category_wrappers), main_category_name, main_category_url)

        
        
    
        has_sub_categories = get_subcategories(main_category_url, main_category_name)
        if not has_sub_categories:
            if SHOW_PRINTS:
                print("No Subs, Füge Main-Seit als URl hinzu")
            categories.append({"url" : main_category_url, "category" : main_category_name})
        if SHOW_PRINTS:
            print("____________________________________________________________________________________________________________________________")

def get_subcategories(url, main_category_name):
    global categories
    #test
    #url= "https://www.medikamente-per-klick.de/blutdruck"
    s = requests.Session()
    s.headers = headers
    source = s.get(url, headers = headers).text
    soup = BeautifulSoup(source, "lxml")

    # with open("testi2.html", "w", encoding="UTF-8") as file:
    #     file.write(soup.prettify())
    
    subcategory_wrappers = soup.find_all("li", class_ ="level02")
    subcategory_wrappers.extend(soup.find_all("li", class_="level03 link"))
    subcategory_wrappers.extend(soup.find_all("li", class_="level04 link"))

    if len(subcategory_wrappers) > 0:
        for sub_category in subcategory_wrappers:
            sub_category_name = sub_category.text.strip()
            sub_category_url = sub_category.find("a").get("href")
            if SHOW_PRINTS:
                print("  --", sub_category_name.strip().replace("  ", "").replace("\n", " "), sub_category_url)

            has_level_02_categories = get_subcategories_02(sub_category_url, main_category_name)

            to_append = {"url" : sub_category_url, "category" : main_category_name}
            if not has_level_02_categories:
                if to_append not in categories:
                    categories.append(to_append)
                    if SHOW_PRINTS:
                        print("     No Sub02, Füge sub category URl hinzu")
                else:
                    if SHOW_PRINTS:
                        print("    ", sub_category_name, "bereits in Liste")
          
          
        return True
    else:
        return False
    
def get_subcategories_02(url_sub, main_category_name):
    global categories
    #test

    # print("  ", url_sub)
    #url= "https://www.medikamente-per-klick.de/blutdruckmessgeraete"
    s = requests.Session()
    s.headers = headers
    source = s.get(url_sub, headers = headers).text
    soup = BeautifulSoup(source, "lxml")

    # with open("testi3.html", "w", encoding="UTF-8") as file:
    #     file.write(soup.prettify())
    
    subcategory_02_wrappers = soup.find_all("li", class_ ="level03 link")

    ################ WEIL IM QUELLCODE NICHT SAUBER GETRENNT #########################
    subcategory_02_wrappers.extend(soup.find_all("li", class_="level04 link"))
    subcategory_02_wrappers.extend(soup.find_all("li", class_="level05 link"))

    if len(subcategory_02_wrappers) > 0:
        for sub_category_02 in subcategory_02_wrappers:
            sub_category_02_name = sub_category_02.text.strip()
            sub_category_02_url = sub_category_02.find("a").get("href")

            has_level_03_categories = get_subcategories_02(sub_category_02_url, main_category_name)

            to_append = {"url" : sub_category_02_url, "category" : main_category_name}
            if not has_level_03_categories:
                if to_append not in categories:
                    categories.append(to_append)
                    if SHOW_PRINTS:
                        print("              No Sub03, Füge sub02", sub_category_02_name, "  URL hinzu:", sub_category_02_url)
                else:
                    if SHOW_PRINTS:
                        print("             ", sub_category_02_name, "bereits in Liste")
            
           
        return True
    else:
        return False
    
def get_subcategories_03(url_sub, main_category_name):
    global categories
    s = requests.Session()
    s.headers = headers
    source = s.get(url_sub, headers = headers).text
    soup = BeautifulSoup(source, "lxml")

    # with open("testi3.html", "w", encoding="UTF-8") as file:
    #     file.write(soup.prettify())
    
    subcategory_03_wrappers = soup.find_all("li", class_ ="level04 link")

    if len(subcategory_03_wrappers) > 0:
        for sub_category_03 in subcategory_03_wrappers:
            sub_category_03_name = sub_category_03.text.strip()
            sub_category_03_url = sub_category_03.find("a").get("href")
            if SHOW_PRINTS:
                print("                  ------ füge sub03 URL hinzu", sub_category_03_name, sub_category_03_url)
            to_append = {"url" : sub_category_03_url, "category" : main_category_name}
            if to_append not in categories:
                categories.append(to_append)
            
        return True
    else:
        return False

def get_pages(url):

    url_to_find = url + "?VIEW_SIZE=100&VIEW_INDEX=1&filterBy=default&sortBy=default"
    product_per_page = 100

    try:
        s = requests.Session()
        s.headers = headers
        source = s.get(url_to_find, headers = headers).text
        soup = BeautifulSoup(source, "lxml")

        # with open("testiproduct.html", "w", encoding="UTF-8") as file:
        #     file.write(soup.prettify())
        
        products_wrapper = soup.find("div", class_ ="displayPagination")
        if len(products_wrapper) == 0:
            print("FIND PAGE: NO PRODUCT WRAPPER!")

        try:
            products = products_wrapper.find("label").text.strip()
            # if SHOW_PRINTS:
            #     print(url)
            #     print("products:", products)
            
            products = int(products.split("von")[-1].strip())
            

            # if SHOW_PRINTS:
            #     print("FOUND PRODUCTS:", products)
            
            pages = products // product_per_page
        
            if products %product_per_page != 0:
                pages += 1
        except Exception as ex:
              print("FIND PAGE: NO PAGE CALCULATION POSSIBLE BECAUSE:", ex)
              raise Exception("no calculation possible)")
        
        #print("PAGES:", pages)
        return pages
    except Exception as e:
        print("no page finding possible!")
        print(e)
        print(url_to_find)
        return -1

def get_product_from_page(url, category):
    global found_products

    pages = get_pages(url)
    if pages == -1:
        return

    for page in range(1, pages +1):
        if SHOW_PRINTS:
            print("Get all products from page", page, "of", pages)
        url_to_scrawl = url+"?VIEW_SIZE=20&VIEW_INDEX="+str(page)+"&filterBy=default&sortBy=default"

        s = requests.Session()
        s.headers = headers
        source = s.get(url_to_scrawl, headers = headers).text
        soup = BeautifulSoup(source, "lxml")

        # with open("testiproduct.html", "w", encoding="UTF-8") as file:
        #     file.write(soup.prettify())

        product_wrappers = soup.find_all("div", class_ ="boxProduct")

        for product_wrapper in product_wrappers:
            try:
                original_link = product_wrapper.find("a").get("href")
                possible_names = product_wrapper.find_all("span")
                for possible_name in possible_names:
                    if possible_name.get("itemprop") == "name":
                        name = possible_name.text.strip()
                        break
                id = product_wrapper.find("dd", class_ ="pzn").text.strip()
                price = product_wrapper.find("dd", class_ ="yourPrice").text.strip().replace("€", "").replace("*", "")

                baseprice = product_wrapper.find("dd", class_ ="groundPrice")
                if baseprice != None:
                    baseprice = baseprice.text
                    baseprice_split = baseprice.split("/")
                    baseprice = baseprice_split[0].strip().replace("€", "").replace("*", "")
                    unit = baseprice_split[1].strip()
                else:
                    baseprice = price
                    unit = "Artikel"

                #print(name, id,  price, baseprice, unit, original_link)
                new_dict = {
                    "id" : id,
                    "unit" : unit,
                    "price" : price, 
                    "baseprice" : baseprice,
                    "category" : category,
                    "imageURL" : "#",
                    "original_link" : original_link,
                    "name" : name
                }

                if new_dict not in found_products:
                   
                    found_products.append(new_dict)
               
            except Exception as e:
                continue


def get_products_from_shop():
    global categories
    get_categories()
    current = 0
    print("Get Product Infos")
    for page in categories[6:]:
        current += 1
        if SHOW_PRINTS:
            print(current, "of", len(categories))
        if SHOW_PRINTS:
            print(page)
        
        get_product_from_page(page["url"], page["category"])
        
        if SHOW_PRINTS:
            print("____________________________________")

    return found_products

def blop(url = "https://www.medikamente-per-klick.de/boots-laboratories?VIEW_SIZE=100&VIEW_INDEX=1&filterBy=default&sortBy=default"):
    s = requests.Session()
    s.headers = headers
    source = s.get(url, headers = headers).text
    soup = BeautifulSoup(source, "lxml")

    with open("blop.html", "w", encoding="UTF-8") as file:
        file.write(soup.prettify())
#get_products_from_shop()

if SHOW_PRINTS:
    print("done")




get_products_from_shop()