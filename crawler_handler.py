
import time
import re
import os
from datetime import datetime
import json
import paramiko
import requests
import secret
try:
    import mapper
except:
    from . import mapper

class CrawlerHandler:
    def __init__(self, store, mapping_cat=mapper.mapping, with_id=False, show_prints=True):
        self.t0 = time.time()
        self.STORE_JSON = {}
        self.STORE_JSON_CURRENT_PRODUCTS = []
        self.STORE_JSON_CURRENT_IDS = []
        self.NEW_ADDED_IDS = []
        self.with_id = with_id
        self.show_prints = show_prints
        self.store = store
        self.updated = 0
        self.new = 0
        self.added_ids = 0
        self.outlier_list = []
        self.max_length = 0
        self.outliers = 0
        self.not_cleaned_prices = 0
        self.mapping_cat = mapping_cat
        self.path_to_store_json = ""
        self.mapper_categories = {
            "drogerie": mapper.mapping_drogerie,
            "baumarkt": mapper.mapping_baumarkt,
            "biocompany": mapper.mapping_biocompany,
            "rewe": mapper.mapping_rewe,
            "ikea": mapper.mapping_ikea,
            "superstore": mapper.mapping_superstore,
            "kaufland_api": mapper.mapping_kaufland_api,
            "dm": mapper.mapping_dm,
            "mueller_api": mapper.mapping_mueller_api,
            "aldisued": mapper.mapping_aldisued,
            "fressnapf_api": mapper.mapping_fressnapf_api,
            "babywalz_api": mapper.mapping_babywalz_api,
            "shopapotheke": mapper.mapping_apotheke,
            "dummy_store_type": mapper.dummy_store_type,
            "lego" : mapper.mapping_lego,
            "medikamente" : mapper.mapping_medikamente,
            "lidl" : mapper.mapping_Lidl_api
        }
        self.path_to_log = ""

        if self.show_prints:
            print("\n\n")
            print("##############################################")
            print("######## START ###############################")
            print("##############################################")

        try:
            self.mapping = self.mapper_categories[self.mapping_cat]
        except:
            if self.show_prints:
                print("Found no special mapping, use default mapping")
            self.mapping = mapper.mapping

        try:
            self.PRODUCTS_TO_CHECK = list(self.mapping.keys())
        except:
            pass

        # quick and dirty solution for different paths in Flask / local
        cwd = os.getcwd()
        if self.show_prints:
            print(cwd)
        
        # pythonAnywhere
        if "SebastianChristoph" in cwd:
            # flask path
            if self.show_prints:
                print("RUNNING IN FLASK")
            self.path_to_store_json = "/home/SebastianChristoph/mysite/static/crawler/jsons/" + self.store + ".json"
            self.path_to_log = "/home/SebastianChristoph/mysite/static/crawler/logging/log.json"
        
        #Raspberry pi
        else:
            if self.show_prints:
                print("RUNNING LOCALLY RASPBERRY")
            self.path_to_store_json = "/home/pi/crawler/jsons/" + self.store + ".json"
            self.path_to_log = "/home/pi/crawler/logging/log.json"
        
        # method calls
        self.current_date = self.get_current_date()
        self.getting_store_json()
        self.get_all_products_form_JSON()

    def print_message(self, message):
        done_position = 70
        message_length = len(message)
        padding = done_position - message_length
        dots = '.' * padding
        if self.show_prints:
            print(message + dots, end="")

    def getting_store_json(self):
        self.print_message("Getting Store JSON for " + self.store)
        with open(self.path_to_store_json, encoding="utf-8") as json_file:
            self.STORE_JSON = json.load(json_file)
        if self.show_prints:
            print("Done")

    def get_current_time(self):
        current_time = datetime.now()
        current_time_format = current_time.strftime("%d-%m  %H:%M")
        return current_time_format

    def get_current_date(self):
        today = datetime.now()
        return today.strftime("%d-%m-%Y")

    def get_all_products_form_JSON(self):
        error_loading_ids = 0
        if self.with_id:
            if self.show_prints:
                self.print_message("Getting IDs from STORE_JSON...")
            for product in self.STORE_JSON["products"]:
                if product.get("id") != None:
                    self.STORE_JSON_CURRENT_IDS.append(product["id"])
                    self.added_ids += 1
                else:
                    error_loading_ids += 1

            if self.show_prints:
                print("Done")
                print("   Already", len(self.STORE_JSON_CURRENT_IDS),
                      "IDs in json, errors in loading ids:", error_loading_ids)

        # HANDLE PRODUCT NAMES
        else:
            self.print_message("Getting products from STORE_JSON...")
            for product in self.STORE_JSON["products"]:
                self.STORE_JSON_CURRENT_PRODUCTS.append(product["name"])
            if self.show_prints:
                print("Done")

    def is_product_already_in_json(self, product):
        return product in self.STORE_JSON_CURRENT_PRODUCTS

    def is_product_id_already_in_json(self, product_id):
        return product_id in self.STORE_JSON_CURRENT_IDS

    def is_product_already_in_dict(self, product):
        return product in self.STORE_JSON["products"]

    def get_file_size(self, path):
        file_size_in_bytes = os.path.getsize(path)
        file_size_in_mb = file_size_in_bytes / (1024 * 1024)
        return file_size_in_mb

    def save_data(self):
        self.print_message("Save data to " + self.store + ".json ...")
        if self.store == "Testing":
            with open("testingoutput.json", 'w', encoding="utf-8") as textfile:
                json.dump(self.STORE_JSON, textfile, sort_keys=True, indent=4)
        else:
            with open(self.path_to_store_json, 'w', encoding="utf-8") as textfile:
                json.dump(self.STORE_JSON, textfile, sort_keys=True, indent=4)

        if "SebastianChristoph" not in self.path_to_store_json:
            self.upload_json()

        if self.show_prints:
            print("Done")

    def clean_price_text(self, price_text):
        try:

            cleaned_price = str(price_text)
            cleaned_price = cleaned_price.replace(",", ".")

            if "=" in cleaned_price:
                cleaned_price = cleaned_price.split("=")[-1]

            match = re.search(r'\d+(\.\d*)?', cleaned_price)

            if match:
                cleaned_price = match.group()
                cleaned_price = float(cleaned_price)
                cleaned_price = round(cleaned_price, 2)
                cleaned_price = format(cleaned_price, '.2f')
                if (cleaned_price[-1] == "."):
                    cleaned_price = cleaned_price[:-1]

                return cleaned_price
            else:
                print("No cleaning possible for:", price_text)
                self.not_cleaned_prices += 1
                return "0"

        except Exception as e:
            if self.show_prints:
                print("ERROR IN CLEANING")
                print(e)
                print("PRICE IN:", price_text,
                      " / PRICE IN TYPE:", type(price_text))
                print("----------------")
            return "0"

    def clean_name(self, name):

        forbidden_characters = ["%", "|", '"', "&", "\\", "/", "#"]

        for char in forbidden_characters:
            name = name.replace(char, "")

        name = name.replace("  ", " ")

        return name

    def clean_unit_text(self, unittext):
        return unittext.upper()

    def clean_data(self):
        if self.show_prints:
            self.print_message("Cleaning up")

        for product in self.STORE_JSON["products"]:
            for price_change in product["price_changes"]:
                price_change["price_single"] = self.clean_price_text(
                    price_change["price_single"])
                price_change["price_bulk"] = self.clean_price_text(
                    price_change["price_bulk"])
                product["unit"] = self.clean_unit_text(product["unit"])
                product["name"] = self.clean_name(product["name"])

        if self.show_prints:
            print("Done")

    def handle(self, found_products, product_to_find):
        for found_product in found_products:
            if (self.is_product_already_in_json(found_product["name"])):

                # product already in JSON
                # find it in JSON
                for entry in self.STORE_JSON["products"]:
                    if entry["name"] == found_product["name"]:
                        entry["dates"][self.current_date] = found_product["price"]
                        entry["original_link"] = found_product["original_link"]
                        self.updated += 1
                        break
            else:
                new_product = {
                    "name": found_product["name"],
                    "category": self.mapping[product_to_find],
                    "image": found_product["imageURL"],
                    "dates": {
                        self.current_date:  found_product["price"]
                    },
                    "found_by_keyword": product_to_find,
                    "original_link": found_product["original_link"]
                }

                self.STORE_JSON["products"].append(new_product)
                self.new += 1

    def is_price_change_outlier(self, price_before, price_today):

        threshhold = 125
        try:
            change_in_percent = abs(
                ((float(price_today) - float(price_before)) / float(price_before)) * 100)
            
            if change_in_percent > threshhold:
                print("OUTLIER IN BULK")
                print(price_before, price_today)
                print(change_in_percent)
            return change_in_percent > threshhold
        except:
            return False
    
    def upload_log_json(self):
        print("\nSTART UPLOAD log.json")
        host = "ssh.pythonanywhere.com"
        port = 22
        password = secret.get_password()
        username = secret.get_username()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("..connect")
        ssh.connect(host, port, username, password)

        try:
            sftp = ssh.open_sftp()
            path = "/home/SebastianChristoph/mysite/static/crawler/logging/log.json"
            localpath = "/home/pi/crawler/logging/log.json"
            print("..upload")
            sftp.put(localpath, path)
            sftp.close()
        except Exception as e:
            print("..nope")
            print(e)

        print("..close")
        ssh.close()

        print("UPLOAD log.json SUCCESSFULL")

    def upload_json(self):
       
        print("\nSTART UPLOAD store_json")
        host = "ssh.pythonanywhere.com"
        port = 22
        password = secret.get_password()
        username = secret.get_username()

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("..connect")
        ssh.connect(host, port, username, password)

        try:
            sftp = ssh.open_sftp()
            path = "/home/SebastianChristoph/mysite/static/crawler/jsons/" + self.store + ".json"
            localpath = "/home/pi/crawler/jsons/" + self.store + ".json"
            print("..upload")
            sftp.put(localpath, path)
            sftp.close()
        except Exception as e:
            print("..nope")
            print(e)

        print("..close")
        ssh.close()

        print("UPLOAD store_json SUCCESSFULL")

    def handle_with_id(self, found_products, product_to_find="no data"):

        for found_product in found_products:

            if found_product.get("category") != None:
                cat = found_product["category"]
            else:
                cat = self.mapping[product_to_find]

            name = self.clean_name(found_product["name"])

            if found_product["id"] in self.NEW_ADDED_IDS:
                continue

            # ID already in JSON ;
            if (self.is_product_id_already_in_json(found_product["id"])):

                # find ID in JSON
                for product_in_json in self.STORE_JSON["products"]:
                    if product_in_json["id"] == found_product["id"]:

                        # update image
                        product_in_json["imageURL"] = found_product["imageURL"]

                        # update category
                        product_in_json["category"] = cat

                        # HAT BEREITS EINTRAG VON HEUTE?
                        if product_in_json["price_changes"][-1]["date"] == self.get_current_date():
                            continue

                        # get last price-change
                        last_price_bulk = product_in_json["price_changes"][-1]["price_bulk"]
                        last_price_single = product_in_json["price_changes"][-1]["price_single"]

                        if self.is_price_change_outlier(price_before=self.clean_price_text(
                            last_price_bulk), price_today=self.clean_price_text(found_product["baseprice"])):
                            self.outliers += 1
                            #print("FOUND OUTLIER")

                            outlier_info = {
                                "price_before_bulk": last_price_bulk, 
                                "price_before_single" : last_price_single,
                                "price_today_single" : found_product["price"],
                                "price_today_bulk" : found_product["baseprice"],
                                "product" : found_product,
                                "store" : self.store

                            }

                            self.outlier_list.append(outlier_info)
                        
                            continue

                        # new price change
                        if self.clean_price_text(found_product["price"]) != last_price_single:
                            # print(found_product["baseprice"], last_price_bulk)

                            new_price_change = {
                                "date": self.get_current_date(),
                                "price_single": self.clean_price_text(found_product["price"]),
                                "price_bulk": self.clean_price_text(found_product["baseprice"])
                            }

                            product_in_json["price_changes"].append(
                                new_price_change)

                            self.updated += 1
                            self.NEW_ADDED_IDS.append(product_in_json["id"])
                            break

            else:
                new_product = {
                    "id": found_product["id"],
                    "name": name,
                    "category": cat,
                    "unit": found_product["unit"],
                    "imageURL": found_product["imageURL"],
                    "price_changes": [
                        {
                            "date":  self.get_current_date(),
                            "price_single": found_product["price"],
                            "price_bulk": found_product["baseprice"]
                        }
                    ],
                    "original_link": found_product["original_link"]
                }

                if not self.is_product_already_in_dict(new_product) and new_product["id"] not in self.NEW_ADDED_IDS:
                    self.NEW_ADDED_IDS.append(new_product["id"])
                    self.STORE_JSON["products"].append(new_product)
                    self.STORE_JSON_CURRENT_IDS.append(new_product["id"])
                    self.new += 1

    def savelog(self, took_time, not_touched, not_touched_products_percent):
        if self.show_prints:
            print("Saving log")
        filesize = self.get_file_size(self.path_to_store_json)

        current_time = self.get_current_time()

        response = requests.get("https://data.check-die-preise.de/apilog")
        log_dict = json.loads(response.text)

        log_str =f"{self.store.upper()} finished at {current_time}, took {took_time} [{round(filesize,2)}MB] P: {len(self.STORE_JSON['products'])} Upd: {self.updated} Add: {self.new} No data: {not_touched} ({not_touched_products_percent}%) Outlier: {self.outliers}"

        log_dict["crawler_logging"].append(log_str)

        stats_dict = {
                "store" : self.store,
                "finished" : current_time,
                "took" : took_time,
                "filesize" : round(filesize,2),
                "products_total" : len(self.STORE_JSON['products']) + self.outliers,
                "added" : self.new,
                "not_touched" : not_touched,
                "updated" : self.updated,
                "outliers" : self.outliers
        }
        log_dict["crawler_logging_stats"].append(stats_dict)

        print("... adding outliers do log_dict")
        for outlier in self.outlier_list:
            log_dict["outliers"].append(outlier)
        

        if "SebastianChristoph" in self.path_to_log:
            with open(self.path_to_log, "w", encoding="UTF-8") as file:
                json.dump(log_dict, file)
        else:
            with open(self.path_to_log, "w", encoding="UTF-8") as file:
                json.dump(log_dict, file)
            self.upload_log_json()
        print("Done")

    def save_error_log(self):
        self.print_message("Saving error log")

        with open(self.path_to_log, "r", encoding="UTF-8") as file:
            content = file.read()
            log_dict = json.dumps(content)

        error_log_str = "\n-----------------------------------------------------\n" + self.store + " ABORTED WITH ERROR\n"

        log_dict["crawler_logging"].append(error_log_str)
        with open(self.path_to_log, "w", encoding="UTF-8") as file:
            json.dump(log_dict, file, sort_keys=True, indent=4)

        if self.show_prints:
            print("Done saving error message")

    def save_error_to_log(self, error):
        if self.show_prints:
            print("Saving error to log")

        response = requests.get("https://data.check-die-preise.de/apilog")
        log_dict = json.loads(response.text)

        log_str =f"{self.store.upper()} FINISHED WITH ERROR : {error}"
        log_dict["crawler_logging"].append(log_str)

        if "SebastianChristoph" in self.path_to_log:
            with open(self.path_to_log, "w", encoding="UTF-8") as file:
                json.dump(log_dict, file)
        else:
            with open(self.path_to_log, "w", encoding="UTF-8") as file:
                json.dump(log_dict, file)
            self.upload_log_json()
        print("Done")

        
    def give_infos(self):
        self.t1 = time.time()
        sekunden = self.t1-self.t0
        stunden = int(sekunden // 3600)
        minuten = int((sekunden % 3600) // 60)
        restsekunden = int(sekunden % 60)
        formatted_time = f'{stunden:02d}:{minuten:02d}:{restsekunden:02d}'
        not_touched_products = len(
            self.STORE_JSON["products"]) - self.updated - self.new
        not_touched_products_percent = round(not_touched_products/ len(
            self.STORE_JSON["products"]) *100, 1)

        print("\n****************")
        print("FINISHED", self.store, "in", formatted_time, "seconds")
        print("* Products in JSON:", len(self.STORE_JSON["products"]))
        print("     - Updated", self.updated, "products.")
        print("     - Added", self.new, "product to JSON.")
        print("     - no new data for", not_touched_products, "(", not_touched_products_percent, "%) products in JSON.")
        print("     - outliers:", self.outliers)

        file_size_in_bytes = os.path.getsize(self.path_to_store_json)
        file_size_in_mb = file_size_in_bytes / (1024 * 1024)
        print("Size of STORE_JSON:", round(file_size_in_mb, 2), "MB")

        self.savelog(formatted_time, not_touched_products, not_touched_products_percent)
        print("\n\n")