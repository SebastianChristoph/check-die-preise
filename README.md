# check-die-preise.de

## Crawler

Die Crawler-Skripts stellen die Verbindung zwischen dem CrawlerHandler und den einzelnen Scrapern dar. Sie rufen die Scraper auf, empfangen die gefundenen Produkte und übergeben diese an den CrawlerHandler.

## Scraper

Hier passiert die eigentliche Arbeit. Manche Scraper können APIs abgreifen, manche durchsuchen den HTML-Quelltext des jewieligen Stores. 
Am Ende wird dem Crawler-Skript immer ein Liste in folgendem Format übergeben:

```json
[
  {
    "id" : 12345,
    "name" : "product name",
    "price" : 14.6,
    "baseprice":  22.5,
    "unit" : "pro Stk",
    "category" : "Food",
    "original_link" : "link to Webshop",
    "imageURL" : "www..."
  }
]
```

## CrawlerHandler

Der CrawlerHandler liest die bisherigen Produkte der Stores aus der jeweiligen JSON ein, fügt neue Produkte hinzu oder updatet diese, falls es Preis-Änderungen gibt, und speicher die JSON wieder ab bzw lädt sie auf den Server. 
Es finden auch Bereinigungen und Transformationen statt.

## Store Jsons
Diese sind nicht teil dieser Repo, da diese auf einem Server liegen. Diese könenn aber leicht über www.check-die-preise.de/apis abgerufen werden. 
Die Jsons der jeweiligen Stores weisen folgendes Format auf:

```json
{
    "info": "infos about the store",
    "name": "storename",
    "products": [{
        "category": "Lebensmittel",
        "id": 12345,
        "unit": "KG",
        "imageURL": "www.",
        "name": "product name",
        "original_link": "wbeshop link",
        "price_changes": [{
            "date": "29-10-2023",
            "price_bulk": "14.50",
            "price_single": "1.45"
        },
        {
            "date": "31-10-2023",
            "price_bulk": "14.50",
            "price_single": "1.50"
        }],
    }]
}
```


