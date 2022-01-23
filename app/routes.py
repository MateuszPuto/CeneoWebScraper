from re import split
from app import app
from app.models.product import Product
from app.models.analyze import get_charts
from flask import render_template, redirect, url_for, send_from_directory, request
from os import listdir
from functools import reduce
from flask import request

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html.jinja")

@app.route('/search', methods=['POST'])
def search():
    try:
    	id = request.form.get('id')
    	product = Product(id=id)
    	product.importProduct()
    except FileNotFoundError:
        return render_template('index.html.jinja')

    return render_template('product.html.jinja', product=product)

@app.route('/extract', methods=['GET', 'POST'])
def extract():
    try:
        if request.method == 'POST':
            id = request.form.get('id')
            product = Product(id=id)
            product.extractName()
            if product.name is not None:
                product.extractProduct()
                product.exportProduct()
                return redirect(url_for('product', id=id))
            error = "Podana wartość nie jest poprawnym kodem produktu!"
            return render_template('extract.html.jinja', error=error)

        return render_template('extract.html.jinja')
    
    except FileExistsError:
        error = "Produkt o podanym id jest już pobrany."
        return render_template('extract.html.jinja', error=error)

@app.route('/products')
def products():
    productList = []
    for product in listdir("app/products"):
        productId = product.split('.')[0]
        product = Product(id=productId)
        product.importProduct()
        noPros =  reduce(lambda x,y: x+y, [0] + [len(opinion.pros) for opinion in product.opinions])
        noCons = reduce(lambda x,y: x+y, [0] + [len(opinion.pros) for opinion in product.opinions])
        productList.append([product.id, product.name, len(product.opinions), noPros, noCons, product.stars, product.price])

    return render_template("products.html.jinja", products=productList)

@app.route('/about')
def about():
   return render_template('about.html.jinja')

@app.route('/product/<id>')
def product(id):
    product = Product(id=id)
    product.importProduct()
    get_charts(id)

    return render_template('product.html.jinja', product=product)

@app.route('/downloads/<dirname>/<filename>')
def downloadFile(dirname, filename):
    path = f"{dirname}/{filename}"
    return send_from_directory('downloads', path)

@app.route('/charts/<id>')
def charts(id):
    urls = {"id": id, "overview": f'{id}/{id}_overview.txt', "rcmd": f'{id}/{id}_rcmd.png', "stars": f'{id}/{id}_stars.png', "pros": f'{id}/{id}_pros.png', "cons": f'{id}/{id}_cons.png'}

    return render_template('charts.html.jinja', url=urls)
