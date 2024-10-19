import os
import sqlite3

from flask import jsonify, request

from app import app, render_template

conn = sqlite3.connect('databaseVue.db', check_same_thread=False)

UPLOAD_FOLDER = 'static/uploads/'  # Ensure this folder exists
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/add_user_admin', methods=['POST'])
def add_user_admin():
    if 'profile' not in request.files or request.files['profile'].filename == '':
        return jsonify({'error': 'No selected file or file part'}), 400

    file = request.files['profile']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Get other user data from the form
    data = request.form
    code = data['code']
    name = data['name']
    password = data['password']
    gender = data['gender']
    role = data['role']
    email = data['email']
    phone = data['phone']
    address = data['address']
    status = data['status']

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user (code, profile, name, password, gender, role, email, phone, address, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (code, filename, name, password, gender, role, email, phone, address, status))
    conn.commit()

    new_user = {
        'id': cursor.lastrowid,
        'code': code,
        'profile': filename,
        'name': name,
        'gender': gender,
        'role': role,
        'email': email,
        'phone': phone,
        'address': address,
        'status': status
    }
    return jsonify(new_user), 201


@app.route('/get_user_by_id/<int:id>', methods=['GET'])
def get_user_by_id(id):
    # Use a parameterized query for SQLite
    sql = """
        SELECT id, code, name, email, phone, address, gender, role, status, password, profile
        FROM user
        WHERE id = ?;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (id,))  # Use parameterized query with SQLite
        user_data = cursor.fetchone()  # Fetch one record from the query result

        if user_data:
            profile_image_url = None
            if user_data[10]:  # Access the 'profile' field by index 10
                profile_image_url = f"/static/uploads/{user_data[10]}"  # Prefix with static folder path

            # Return the user data as a JSON response
            return jsonify({
                'id': user_data[0],  # Access id field (index 0)
                'code': user_data[1],  # Access code field (index 1)
                'name': user_data[2],  # Access name field (index 2)
                'email': user_data[3],  # Access email field (index 3)
                'phone': user_data[4],  # Access phone field (index 4)
                'address': user_data[5],  # Access address field (index 5)
                'gender': user_data[6],  # Access gender field (index 6)
                'role': user_data[7],  # Access role field (index 7)
                'status': user_data[8],  # Access status field (index 8)
                'password': user_data[9],  # Access password field (index 9)
                'profile': profile_image_url  # Use profile image URL (index 10)
            })
        else:
            # If no user is found with the given id
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        # Handle any exceptions that may occur during the query execution
        return jsonify({'error': str(e)}), 500


@app.route('/update_user/<int:id>', methods=['PUT'])
def update_user(id):
    cursor = conn.cursor()

    # Get other user data from the form
    data = request.form
    code = data['code']
    name = data['name']
    email = data['email']
    phone = data['phone']
    address = data['address']
    gender = data['gender']
    role = data['role']
    status = data['status']

    # Handle file upload (optional)
    if 'profile' in request.files and request.files['profile'].filename != '':
        file = request.files['profile']
        if allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Update the profile image in the database
            cursor.execute("UPDATE user SET profile = ? WHERE id = ?", (filename, id))

    # Update other user fields in the database
    cursor.execute("""
        UPDATE user
        SET code = ?, name = ?, email = ?, phone = ?, address = ?, gender = ?, role = ?, status = ?
        WHERE id = ?
    """, (code, name, email, phone, address, gender, role, status, id))

    conn.commit()

    return jsonify({'id': id, 'message': 'User updated successfully'})


@app.route('/delete_user/<int:id>', methods=['DELETE'])
def delete_user_admin(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user WHERE id = ?", (id,))
    conn.commit()

    return jsonify({'message': 'User deleted successfully'})


@app.route('/get_users', methods=['GET'])
def get_users_admin():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, code, profile, name, email, phone, gender, role, status
        FROM user
    """)
    rows = cursor.fetchall()

    users = []
    for item in rows:
        profile_image = item[2] if item[2] else 'no_image'  # Handle missing image
        users.append({
            'id': item[0],
            'code': item[1],
            'profile': profile_image,
            'name': item[3],
            'email': item[4],
            'phone': item[5],
            'gender': item[6],
            'role': item[7],
            'status': item[8],
        })

    return jsonify(users)


@app.route('/admin')
def admin():
    return render_template("admin/dashboard.html", module='admin')


@app.route('/user_home')
def user_home():
    return render_template("admin/user.html", module='user_home')


@app.route('/list_product_admin')
def list_product_admin():
    return render_template("admin/add_product.html", module='list_product_admin')


@app.route('/add_product_admin', methods=['POST'])
def add_product_admin():
    if 'image' not in request.files or request.files['image'].filename == '':
        return jsonify({'error': 'No selected file or file part'}), 400

    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Get other product data from the form
    data = request.form
    code = data['code']
    name = data['name']
    category_id = data['category_id']
    cost = data['cost']
    price = data['price']
    current_stock = data['current_stock']

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO product (code, image, name, category_id, cost, price, current_stock)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (code, filename, name, category_id, cost, price, current_stock))
    conn.commit()

    new_product = {
        'id': cursor.lastrowid,
        'code': code,
        'image': filename,
        'name': name,
        'category_id': category_id,
        'cost': cost,
        'price': price,
        'current_stock': current_stock
    }
    return jsonify(new_product), 201


@app.route('/update_product/<int:id>', methods=['PUT'])
def update_product(id):
    cursor = conn.cursor()

    # Get other product data from the form
    data = request.form
    code = data['code']
    name = data['name']
    category_id = data['category_id']
    cost = data['cost']
    price = data['price']
    current_stock = data['current_stock']

    # Handle file upload
    if 'image' in request.files and request.files['image'].filename != '':
        file = request.files['image']
        if allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute("UPDATE product SET image = ? WHERE id = ?", (filename, id))

    cursor.execute("""
        UPDATE product
        SET code = ?, name = ?, category_id = ?, cost = ?, price = ?, current_stock = ?
        WHERE id = ?
    """, (code, name, category_id, cost, price, current_stock, id))
    conn.commit()

    return jsonify({'id': id, 'message': 'Product updated successfully'})


@app.route('/delete_product/<int:id>', methods=['DELETE'])
def delete_product_admin(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product WHERE id = ?", (id,))
    conn.commit()

    return jsonify({'message': 'Product deleted successfully'})


@app.route('/get_products', methods=['GET'])
def get_products_admin():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.code, p.name, p.cost, p.price, p.current_stock, p.image, p.category_id, c.name AS category_name 
        FROM product p
        JOIN category c ON p.category_id = c.id
    """)
    rows = cursor.fetchall()

    products = []
    for item in rows:
        image = item[6] if item[6] else 'no_image'  # Handle missing image
        products.append({
            'id': item[0],
            'code': item[1],
            'name': item[2],
            'cost': item[3],
            'price': item[4],
            'current_stock': item[5],
            'image': image,
            'category_id': item[7],  # Include category ID for editing
            'category_name': item[8],  # Include category name
        })

    return jsonify(products)


@app.route('/category_admin')
def add_category_admin():
    module = 'add_category_admin'
    return render_template("admin/category.html", module=module)


@app.route('/get_categories', methods=['GET'])
def get_categories():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM category")
    rows = cursor.fetchall()

    categories = []
    for row in rows:
        categories.append({
            'id': row[0],
            'name': row[1],
            'description': row[2],
        })
    return jsonify(categories)


@app.route('/add_category', methods=['POST'])
def add_category():
    data = request.get_json()
    name = data['name']
    description = data['description']

    cursor = conn.cursor()
    cursor.execute("INSERT INTO category (name, description) VALUES (?, ?)", (name, description))
    conn.commit()

    new_category = {
        'id': cursor.lastrowid,
        'name': name,
        'description': description
    }
    return jsonify(new_category)


# Route to update an existing category
@app.route('/update_category/<int:id>', methods=['PUT'])
def update_category(id):
    data = request.get_json()
    name = data['name']
    description = data['description']

    cursor = conn.cursor()
    cursor.execute("UPDATE category SET name = ?, description = ? WHERE id = ?", (name, description, id))
    conn.commit()

    return jsonify({'id': id, 'name': name, 'description': description})


# Route to delete a category
@app.route('/delete_category/<int:id>', methods=['DELETE'])
def delete_category(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM category WHERE id = ?", (id,))
    conn.commit()

    return jsonify({'message': 'Category deleted successfully'})
