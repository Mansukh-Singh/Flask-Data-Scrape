from flask import Flask, render_template, url_for, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["Book_Scrape"]
collection = db["Book_Data"]

global bookname
bookname = []

app = Flask(__name__)

@app.route("/", methods = ["GET","POST"])
def home():
    global bookname
    variable = ''
    if request.method == "POST":
        name = request.form["text"]
        if name == "mongoDB":
            if bookname:
                book_data = {}
                book_data['name'] = bookname[0]
                book_data['price'] = bookname[1]
                book_data['description'] = bookname[2]
                book_data['upc'] = bookname[3]
                book_data['stars'] = bookname[4]
                book_data['reviews'] = bookname[5]
                print(book_data)
                collection.insert_one(book_data)
                bookname = []
                variable = "Data Inserted into MongoDB"
            else:
                variable = "Does not have any scraped data to insert into MongoDB !"
        else:
            url = f'https://books.toscrape.com/catalogue/{name}/index.html'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            bookname.append(soup.find(class_ = 'col-sm-6 product_main').find('h1').text)   
            bookname.append(soup.find(class_ = 'col-sm-6 product_main').find(class_ = "price_color").text[1:]) 
            bookname.append(soup.find(class_ = 'product_page').find_all('p')[3].text)
            bookname.append(soup.find(class_ = 'table table-striped').find_all('td')[0].text)
            bookname.append(str(soup.find(class_ = "col-sm-6 product_main").find_all('p')[2]).split('>')[0][::-1].split()[0][::-1][0:-1])
            bookname.append(soup.find(class_ = 'table table-striped').find_all('td')[-1].text)
    return render_template('page.html',bookname=bookname,variable=variable)

if __name__ == "__main__":
    app.run(debug = True)