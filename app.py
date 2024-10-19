from datetime import datetime, date
import timestamp as timestamp
from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
import requests
# from PIL import Image
from io import BytesIO
import time
import os
import sqlite3



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/image'

conn = sqlite3.connect('database.db', check_same_thread=False)

bot_token = "6678957147:AAEoRzWc0YFs0twjzAA_EPtd5zh9y4C9G44"
chat_id = "5130480074"

product_list = [
    {
        'id': '1',
        'title': 'Long Sleeve',
        'price': '99.19',
        'description': 'Cozy, Warm, Hype',
        'image': 'hm1-2.png',
        'discount': '150.90'
    },
    {
        'id': '2',
        'title': 'Long Sleeve Grey',
        'price': '30.60',
        'description': 'Cozy, Warm, Hype',
        'image': 'hm2-2.png',
        'discount': '50.90'
    },
    {
        'id': '3',
        'title': 'Long Black Sleeve',
        'price': '39.60',
        'description': 'Cozy, Warm, Hype',
        'image': 'hm3-1.png',
        'discount': '50.90'
    },
    {
        'id': '4',
        'title': 'Long Shirt',
        'price': '89.60',
        'description': 'Warm, Hype',
        'image': 'hm4-2.png',
        'discount': '150.90'
    }
]


import routes


@app.route('/')
def home():
    return render_template("index.html", active_page='home')


@app.get('/login')
def login():
    return render_template("login.html")


@app.get('/signup')
def signup():
    return render_template("signup.html")


@app.get('/clothes')
def clothes():
    return render_template("clothes.html", active_page='clothes')


@app.get('/about')
def about():
    return render_template("aboutus.html", active_page='about')


@app.get('/product')
def product():
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
    product = response.json()
    product_list = product
    return render_template("product.html", active_page='product', product_list=product_list)


@app.get('/product_detail')
def product_detail():
    product_id = request.args.get('id')
    url = "https://fakestoreapi.com/products/{}".format(product_id)
    response = requests.get(url)
    current_product = []
    current_product = response.json()
    return render_template('product_detail.html', current_product=current_product)


@app.post('/checkout')
def checkout():
    product_id = request.form.get('id')
    quantity = request.form.get('quantity')
    url = "https://fakestoreapi.com/products/{}".format(product_id)
    response = requests.get(url)
    current_product = []
    current_product = response.json()
    return render_template('checkout.html', current_product=current_product, quantity=quantity)


# @app.post('/submit_order')
# def submit_order():
#     product_id = request.form.get('product_id')
#     url = f"https://fakestoreapi.com/products/{product_id}"
#     response = requests.get(url)
#     current_product = response.json()
#
#     image_url = current_product.get('image')
#     image_response = requests.get(image_url)
#     if image_response.status_code == 200:
#         # image = Image.open(BytesIO(image_response.content))
#
#         new_width = 250
#         aspect_ratio = image.height / image.width
#         new_height = int(new_width * aspect_ratio)
#         resized_image = image.resize((new_width, new_height))
#
#         image_bytes = BytesIO()
#         resized_image.save(image_bytes, format='JPEG')
#         image_bytes.seek(0)
#     else:
#         raise Exception(f"Failed to fetch image from {image_url}")
#
#     name = request.form.get('username')
#     phone = request.form.get('phone')
#     location = request.form.get('location')
#     # quantity = 5
#     quantity = request.form.get('quantity')
#     price = float(current_product["price"])
#     quantity = int(quantity)
#     html = (
#         "<strong>🧾 {inv_no}</strong>\n"
#         "<code>📆 {date}</code>\n"
#         "<code>============================</code>\n"
#         "<code>ID\t\tQuality\t\tPrice\t\tAmount</code>\n"
#     ).format(
#         inv_no='INV0001',
#         date=date.today(),
#     )
#     html += (
#         f"<code>{current_product['id']}\t\t\t\t{quantity}\t\t\t\t${current_product['price']}\t\t\t\t${current_product['price']}</code>\n"
#     )
#     html += (
#         "<code>-----------------------------</code>\n"
#         "<code>Customer: {name}</code>\n"
#         "<code>Phone Number: {phone}</code>\n"
#         "<code>Location: {location}</code>\n"
#         "<code>Item: {product}</code>\n"
#         "<code>Total: ${total}</code>\n"
#         "<code>Grand Total: ${grand_total}</code>\n"
#
#     ).format(
#         name=f'{name}',
#         phone=f'{phone}',
#         location=f'{location}',
#         quantity=f'{quantity}',
#         product=f'{" ".join(current_product["title"].split()[0:3])}',
#         total=f'{current_product["price"]}',
#         grand_total=price * quantity,
#     )
#
#     url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
#     files = {'photo': ('image.jpg', image_bytes, 'image/jpeg')}
#     data = {'chat_id': chat_id, 'caption': html, 'parse_mode': 'HTML'}
#     response = requests.get(url, files=files, data=data)
#
#     time.sleep(5)
#
#     return render_template('submit_order.html', current_product=current_product, name=name, phone=phone,
#                            location=location, quantity=quantity)


@app.get('/add_product')
def add_product():
    return render_template('addproduct.html')


@app.get('/productdb')
def productdb():
    row = conn.execute("""SELECT * FROM product""")
    product = []
    for item in row:
        image = ''
        if item[6] == None:
            image = 'no_image'
        else:
            image = item[6]
        product.append(
            {
                'id': item[0],
                'title': item[1],
                'cost': item[2],
                'price': item[3],
                'description': item[4],
                'image': image,
            }
        )
    return render_template('productdb.html', data=product, active_page='productdb')


@app.post('/submit_new_product')
def submit_new_product():
    product_id = request.form.get('product_id')
    title = request.form.get('title')
    price = request.form.get('price')
    cost = request.form.get('cost')
    category = request.form.get('category')
    description = request.form.get('description')

    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'] + '/product', file.filename))

    res = conn.execute(
        f"""INSERT INTO `product` VALUES (null, '{title}', '{price}', '{cost}', '{category}', '{description}', '{file.filename}')""")
    conn.commit()
    return redirect(url_for('add_product'))


@app.post('/delete_product')
def delete_product():
    product_id = request.form.get('product_id')
    res = conn.execute("""DELETE FROM product WHERE id = ?""", (product_id,))
    conn.commit()
    return redirect(url_for('productdb'))


@app.get('/edit_product')
def edit_product():
    product_id = request.args.get('id')
    row = conn.execute("""SELECT * FROM product where id =?""", (product_id,))
    product = {}
    for item in row:
        image = ''
        if item[6] == None:
            image = 'no_image'
        else:
            image = item[6]
        product ={
                'id': item[0],
                'title': item[1],
                'cost': item[2],
                'price': item[3],
                'category': item[4],
                'description': item[5],
                'image': image,
            }
    return render_template('updateproduct.html', product=product)


@app.post('/update')
def update():
    product_id = request.form.get('product_id')
    image_name = ''

    title = request.form.get('title')
    price = request.form.get('price')
    category = request.form.get('category')
    description = request.form.get('description')

    file = request.files['file']
    file_name= file.filename
    file_path=""
    if file != "":
        file_path = os.path.join(app.config['UPLOAD_FOLDER'] + '/product/', file.filename)

    if not os.path.exists(file_path):
        file.save(file_path)
    file = conn.execute("""SELECT image FROM product where id =?""", (product_id,))
    for item in file:
        if item[0] is not None:
            image_name = item[0]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'] + '/product/', image_name)
            # if os.path.exists(file_path):
            #     os.remove(file_path)

    res = conn.execute(
        f"""UPDATE `product` SET title = '{title}', price = {price}, category = '{category}
            ', description = '{description}', image= '{file_name}' where id ={product_id}""")
    conn.commit()
    return redirect(url_for('productdb'))


@app.get('/test')
def test():
    name = "Goodnight"
    comment = "{# comment #}"
    avg = 50
    numbers = [1, 2, 3, 4, 5, 6]
    model = {
        'name': 'MSI',
        'color': 'Grey'
    }
    foods = ['Apple', 'Burger', 'Brocoli']
    current_hour = datetime.now().hour
    current_time = datetime.now()
    items = [
        {'name': 'Item 1', 'type': 'Fruit'},
        {'name': 'Item 2', 'type': 'Vegetable'},
        {'name': 'Item 3', 'type': 'Fruit'},
        {'name': 'Item 4', 'type': 'Meat'},
        {'name': 'Item 5', 'type': 'Vegetable'},
        {'name': 'Item 6', 'type': 'Grain'},
        {'name': 'Item 7', 'type': 'Fruit'}
    ]
    my_dict = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }
    # group 9 end
    my_list = ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry']
    user = {
        'name': 'Jane Doe',
        'email': 'jane.doe@example.com',
        'phone': '123-456-7890'
    }
    return render_template("test.html",
                           name=name,
                           items=items,
                           comment=comment,
                           avg=avg,
                           numbers=numbers,
                           foods=foods,
                           hour=current_hour,
                           now=current_time,
                           model=model,
                           my_dict=my_dict,
                           my_list=my_list,
                           user=user)


if __name__ == '__main__':
    app.run()
