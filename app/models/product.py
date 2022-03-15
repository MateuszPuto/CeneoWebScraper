from numpy import product
import requests
import json
import os
from bs4 import BeautifulSoup
from app.utils import extractComponent
from app.models.opinion import Opinion 
import pandas as pd# type: ignore
from json2xml import json2xml# type: ignore
from json2xml.utils import readfromstring# type: ignore

class Product:
    def __init__(self, name=None, id=None, stars=None, price=None, opinions=[]):
        self.name = name
        self.id = id
        self.stars = stars
        self.price = price
        self.opinions = opinions.copy()

    def extractName(self):
        respons = requests.get("https://www.ceneo.pl/{}#tab=reviews".format(self.id))
        if respons.status_code == requests.codes.ok:
            pageDOM = BeautifulSoup(respons.text, 'html.parser')
            self.name = extractComponent(pageDOM, '.js_product-h1-link')
            self.stars = extractComponent(pageDOM, 'span.product-review__score', attribute='content')
            self.price = extractComponent(pageDOM, 'span.price')

    def extractProduct(self):
        respons = requests.get("https://www.ceneo.pl/{}#tab=reviews".format(self.id))
        page = 1

        pageDOM = BeautifulSoup(respons.text, 'html.parser')
        downloadedOpinions = 0
            
        while respons.status_code == 200:
            pageDOM = BeautifulSoup(respons.text, 'html.parser')
            opinions = pageDOM.select("div.js_product-review")

            for opinion in opinions:
                self.opinions.append(Opinion().extractOpinion(opinion).transformOpinion())
            downloadedOpinions += len(opinions)
            
            page += 1
            respons = requests.get("https://www.ceneo.pl/{}/opinie-".format(self.id)+str(page), allow_redirects=False)

    def exportProduct(self):
        #create directory
        os.makedirs(f"app/downloads/{self.id}")

        #save json file
        with open(f"app/products/{self.id}.json", "w", encoding="UTF-8") as f:
            json.dump(self.toDict(), f, indent=4, ensure_ascii=False)

        with open(f"app/downloads/{self.id}/{self.id}.json", "w+", encoding="UTF-8") as f:
            json.dump([opinion.toDict() for opinion in self.opinions], f, indent=4, ensure_ascii=False)
        
        #save xml file
        f = open(f"app/products/{self.id}.json", 'r', encoding="UTF-8")
        data =  f.read()
        xml = json2xml.Json2xml(readfromstring(data)).to_xml()
        f.close()
        with open(f"app/downloads/{self.id}/{self.id}.xml", "w", encoding="UTF-8") as f:
            f.write(xml)
        
        #save csv file
        f = open(f"app/products/{self.id}.json", "r", encoding="UTF-8")
        data = json.load(f)
        df = pd.json_normalize(data, 'opinions', ['productId', 'productName', 'stars', 'price'], record_prefix='product_')
        f.close()
        with open(f"app/downloads/{self.id}/{self.id}.csv", "w", encoding="UTF-8") as f:
            f.write(df.to_csv())

    def importProduct(self):
        with open(f"app/products/{self.id}.json", "r", encoding="UTF-8") as f:
            product = json.load(f)
            self.id = product["productId"]
            self.name = product["productName"]
            self.stars = product["stars"]
            self.price = product["price"]
            opinions = product["opinions"]
            for opinion in opinions:
                self.opinions.append(Opinion(**opinion))

    def toDict(self):
        return {
            "productId": self.id,
            "productName": self.name,
            "stars": self.stars,
            "price": self.price,
            "opinions": [opinion.toDict() for opinion in self.opinions]
        }

    def __str__(self) -> str:
        return f"productId: {self.id}<br>productName: {self.name}<br>stars: {self.stars}<br>price: {self.price}<br>opinions<br><br>" + "<br><br>".join(str(opinion) for opinion in self.opinions)

    def __repr__(self) -> str:
        return f"Product(productId={self.id}, productName={self.name}, stars: {self.stars}, price: {self.price}, opinions=[" + ", ".join(opinion.__repr__() for opinion in self.opinions) + "])"

