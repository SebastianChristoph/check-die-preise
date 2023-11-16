
import requests
import json
import random

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}


found_products = []

def get_products_from_shop(hits_max = 30000):
    global found_products
    hits = int(hits_max + random.random() * 2000)

    URL = "https://www.lidl.de/p/api/gridboxes/DE/de/?max="+str(hits)
    s = requests.Session()
    s.headers = headers
    source = s.get(URL, headers = headers).text
    responsedict = json.loads(source)
    
    # with open("lidl.json", "w", encoding="UTF-8") as file:
    #     json.dump(responsedict, file,  sort_keys=True, indent=4)

    print("Found", len(responsedict), "products")

    for product in responsedict:
        try:
            id = product["productId"]
            name = product["fullTitle"]

            try:
                price = product["price"]["price"]
            except:
                continue

            try:
                if product.get("category") != None:
                    if "/" in product["category"]:
                        category = product["category"].split("/")[1]
                    else:
                        category = product["category"]
            except:
                raise Exception("Fehler in Kategorie")
            else:
                category = "Ohne Katgorie"
            original_link = "https://www.lidl.de/" + product["canonicalUrl"]

            try:
                imageURL = product["image"]
            except:
                imageURL = "#"

            try:
                if product["price"].get("basePrice") != None:
                    if "=" in product["price"]["basePrice"]:
                        baseprice_split = product["price"]["basePrice"]["text"].split("=")
                        unit = baseprice_split[0]
                        basePrice = baseprice_split[1]
                    else:
                        unit = product["price"]["basePrice"]["text"]
                        basePrice = price
                else:
                    unit = "pro Artikel"
                    basePrice = price
            except Exception as ex:
                raise Exception("Fehler in Baseprice:", ex)


            new_dict = {
                            "id" : id,
                            "unit" : unit,
                            "price" : price, 
                            "baseprice" : basePrice,
                            "category" : category,
                            "imageURL" : "#",
                            "original_link" : original_link,
                            "name" : name,
                            "imageURL" : imageURL
                        }

            if new_dict not in found_products:                
                found_products.append(new_dict)
        except Exception as e:
            print("error:", e)
            print(product)
            print("_______________________________")
            continue
    
    return found_products

    
                    
      
