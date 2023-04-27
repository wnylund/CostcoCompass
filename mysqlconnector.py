from functools import wraps
import mysql.connector
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'williscool'
bcrypt = Bcrypt(app)

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="manager",
  password="manager",
  database="costco"
)

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_view

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return decorated_view

class AddDeleteForm(FlaskForm):
    # Category table
    category_id = StringField('Category ID')
    category_name = StringField('Category Name')
    category_name_delete = StringField('Category Name')

    #Product 
    product_id = StringField('Product ID')
    category_id_2 = StringField('Category ID')
    name = StringField('Name')
    description = StringField('Description')
    price = StringField('Price')
    name_delete = StringField('Name')

    #Inventory
    product_id_inventory = StringField('Product ID')
    quantity = StringField('Quantity')
    store_id_inventory = StringField('Store ID')
    product_id_inventory_delete = StringField('Product ID')

    #Customer
    customer_id = StringField('Customer ID')
    customer_email = StringField('Email')
    customer_name = StringField('Name')
    customer_name_delete = StringField('Name')
    join_date = StringField('Join Date')

    #Employee (position, email, name, employee_id) 
    position = StringField('Position')
    employee_email = StringField('Email')
    employee_name = StringField('Name')
    employee_id = StringField('Employee ID')
    employee_name_delete = StringField('Name')

    #Product_order (customer_id, order_id, item, status, order_date)
    customer_id_po = StringField('Customer ID')
    order_id = StringField('Order ID')
    item = StringField('Item')
    status = StringField('Status')
    order_date = StringField('Order Date')
    order_id_delete = StringField('Order ID')

    #Sale (store_id, date, sale_id, revenue, quantity)
    store_id_sale = StringField('Store ID')
    sale_date = StringField('Date')
    sale_id = StringField('Sale ID')
    revenue = StringField('Revenue')
    sale_quantity = StringField('Quantity')
    sale_id_delete = StringField('Sale ID')

    #Store_Location (Inventory_id, store_id, contact_info, address)
    inventory_id = StringField('Inventory ID')
    store_id = StringField('Store ID')
    contact_info = StringField('Contact Info')
    address = StringField('Address')
    store_id_delete = StringField('Store ID')

    #User (id, username, isadmin) #HERE
    user_id = StringField('User ID')
    username = StringField('username')
    is_admin = StringField('Is Admin')
    username_set_admin = StringField('Make Admin')
    username_unset_admin = StringField('Make Not Admin')

    
    # Submit buttons
    add_category = SubmitField('Add Category')
    delete_category = SubmitField('Delete Category')

    add_product = SubmitField('Add Product')
    delete_product = SubmitField('Delete Product')

    add_inventory = SubmitField('Add Inventory')
    delete_inventory = SubmitField('Delete Inventory')

    add_customer = SubmitField('Add Customer')
    delete_customer = SubmitField('Delete Customer')

    add_employee = SubmitField('Add Employee')
    delete_employee = SubmitField('Delete Employee')

    add_product_order = SubmitField('Add Product_order')
    delete_product_order = SubmitField('Delete Product_order')

    add_sale = SubmitField('Add Sale')
    delete_sale = SubmitField('Delete Sale')

    add_store_location = SubmitField('Add Store_Location')
    delete_store_location = SubmitField('Delete Store_Location')

    add_user = SubmitField('Add User')
    delete_user = SubmitField('Delete User')
    set_admin = SubmitField('Make Admin')
    unset_admin = SubmitField('Make Not Admin')

@app.route('/')
def index():
    return redirect(url_for('login'))

#EXAMPLE
@app.route("/category", methods=["GET", "POST"])
@login_required
@admin_required
def category():
    form = AddDeleteForm()
    try:
        if form.validate_on_submit():
            mycursor = mydb.cursor()

        # Add/Delete Category
            if form.add_category.data:
                sql = "INSERT INTO Category (category_id, category_name) VALUES (%s, %s)"
                values = (form.category_id.data, form.category_name.data)
                mycursor.execute(sql, values)
                mydb.commit()
            elif form.delete_category.data:
                sql = "DELETE FROM Category WHERE category_name = %s"
                values = (form.category_name_delete.data,)
                mycursor.execute(sql, values)
                mydb.commit()
            return redirect('/category')

        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Category ORDER BY category_id")
        category_data = mycursor.fetchall()

        return render_template('category.html', form=form, category_data=category_data)
    except Exception as e:
        logging.exception('Error in category(): ' + str(e))
        return 'Error: ' + str(e), 500
    
@app.route('/stats')
def stats():
    cursor = mydb.cursor()
    
    # Total number of admin users
    cursor.execute("SELECT COUNT(*) FROM users WHERE isadmin = 1")
    admin_count = cursor.fetchone()[0]

    # Total number of non-admin users
    cursor.execute("SELECT COUNT(*) FROM users WHERE isadmin = 0")
    non_admin_count = cursor.fetchone()[0]

    # Total number of sales
    cursor.execute("SELECT COUNT(*) FROM sale")
    sales_count = cursor.fetchone()[0]

    # Total number of store locations
    cursor.execute("SELECT COUNT(*) FROM store_location")
    store_count = cursor.fetchone()[0]

    # Total number of products
    cursor.execute("SELECT COUNT(*) FROM product")
    product_count = cursor.fetchone()[0]

    cursor.close()

    return render_template('stats.html', admin_count=admin_count,
                           non_admin_count=non_admin_count,
                           sales_count=sales_count,
                           store_count=store_count,
                           product_count=product_count)


@app.route("/inventory", methods=["GET", "POST"])
@login_required
@admin_required
def inventory():
    try:
        form = AddDeleteForm()
        if form.validate_on_submit():
            mycursor = mydb.cursor()
            # Add/Delete Inventory
            if form.add_inventory.data:
                sql = "INSERT INTO Inventory (product_id, quantity, store_id) VALUES (%s, %s, %s)"
                values = (form.product_id_inventory.data, form.quantity.data, form.store_id_inventory.data)
                mycursor.execute(sql, values)
                mydb.commit()
            elif form.delete_inventory.data:
                sql = "DELETE FROM Inventory WHERE product_id = %s"
                values = (form.product_id_inventory_delete.data,)
                mycursor.execute(sql, values)
                mydb.commit()
            return redirect('/inventory')
        mycursor = mydb.cursor()
        
        mycursor.execute("SELECT * FROM Inventory")
        inventory_data = mycursor.fetchall()
        return render_template('inventory.html', form=form, inventory_data=inventory_data) # Pass other table data to the template
    except Exception as e:
        logging.exception('Error in inventory(): ' + str(e))
        return 'Error: ' + str(e), 500
    
def get_product_locations(search_term=None):
    cursor = mydb.cursor()
    print("here 1")
    print("s: ",search_term)
    if search_term:
        sql = """
            SELECT p.product_id, p.name, p.price, s.address, i.quantity
            FROM inventory i
            INNER JOIN product p ON i.product_id = p.product_id
            INNER JOIN store_location s ON i.store_id = s.store_id
            WHERE p.name LIKE %s
            ORDER BY p.name ASC;
        """
        values = ('%' + search_term + '%',)
    else:
        sql = """
            SELECT p.product_id, p.name, p.price, s.address, i.quantity
            FROM inventory i
            INNER JOIN product p ON i.product_id = p.product_id
            INNER JOIN store_location s ON i.store_id = s.store_id
            ORDER BY p.name ASC;
        """
        values = None

    cursor.execute(sql, values)
    results = cursor.fetchall()
    cursor.close()
    return results

@app.route('/customer_view', methods=['GET', 'POST'])
@login_required
def customer_view():
    if request.method == 'POST':
        search_term = request.form['search_term']
        results = get_product_locations(search_term)
    else:
        # Display all products and store locations
        results = get_product_locations()

    return render_template('customer_view.html', results=results)

    
@app.route("/product", methods=["GET", "POST"])
@login_required
@admin_required
def product():
    try:
        form = AddDeleteForm()
        if form.validate_on_submit():
            mycursor = mydb.cursor()
            # Add/Delete Product
            if form.add_product.data:
                sql = "INSERT INTO Product (product_id, category_id, name, description, price) VALUES (%s, %s, %s, %s, %s)"
                values = (form.product_id.data, form.category_id_2.data, form.name.data, form.description.data, form.price.data)
                mycursor.execute(sql, values)
                mydb.commit()
            elif form.delete_product.data:
                sql = "DELETE FROM Product WHERE name = %s"
                values = (form.name_delete.data,)
                mycursor.execute(sql, values)
                mydb.commit()

            return redirect('/product')
        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Product ORDER BY product_id")
        product_data = mycursor.fetchall()

        return render_template('product.html', form=form, product_data=product_data)
    except Exception as e:
        logging.exception('Error in inventory(): ' + str(e))
        return 'Error: ' + str(e), 500

#HERE
@app.route("/customer", methods=["GET", "POST"])
@login_required
@admin_required
def customer():
    form = AddDeleteForm()
    try:
        if form.validate_on_submit():
            mycursor = mydb.cursor()

        # Add/Delete Customer
            if form.add_customer.data:
                print("GOT HERE HECK YEAH2")
                sql = "INSERT INTO Customer (customer_id, email, name, join_date) VALUES (%s, %s, %s, %s)"
                values = (form.customer_id.data, form.customer_email.data, form.customer_name.data, date.today())
                mycursor.execute(sql, values)
                mydb.commit()
            elif form.delete_customer.data:
                sql = "DELETE FROM Customer WHERE name = %s"
                values = (form.customer_name_delete.data,)
                mycursor.execute(sql, values)
                mydb.commit()
            return redirect('/customer')

        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Customer ORDER BY customer_id")
        customer_data = mycursor.fetchall()

        return render_template('customer.html', form=form, customer_data=customer_data)

    except Exception as e:
        logging.exception('Error in customer(): ' + str(e))

#HERE
@app.route("/employee", methods=["GET", "POST"])
@login_required
@admin_required
def employee():
    form = AddDeleteForm()
    try:
        if form.validate_on_submit():
            mycursor = mydb.cursor()
        # Add/Delete employee
            if form.add_employee.data:
                sql = "INSERT INTO Employee (position, email, name, employee_id) VALUES (%s, %s, %s, %s)"
                values = (form.position.data, form.employee_email.data, form.employee_name.data, form.employee_id.data)
                mycursor.execute(sql, values)
                mydb.commit()
            elif form.delete_employee.data:
                sql = "DELETE FROM Employee WHERE name = %s"
                values = (form.employee_name_delete.data,)
                mycursor.execute(sql, values)
                mydb.commit()
            return redirect('/employee')

        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Employee ORDER BY employee_id")
        employee_data = mycursor.fetchall()

        return render_template('employee.html', form=form, employee_data=employee_data)

    except Exception as e:
        logging.exception('Error in employee(): ' + str(e))

#HERE
@app.route("/product_order", methods=["GET", "POST"])
@login_required
@admin_required
def product_order():
    form = AddDeleteForm()
    try:
        if form.validate_on_submit():
            mycursor = mydb.cursor()

        # Add/Delete product_order
            if form.add_product_order.data:
                sql = "INSERT INTO Product_order (customer_id, order_id, item, status, order_date) VALUES (%s, %s, %s, %s, %s)"
                values = (form.customer_id_po.data, form.order_id.data, form.item.data, form.status.data, form.order_date.data)
                mycursor.execute(sql, values)
                mydb.commit()
            elif form.delete_product_order.data:
                sql = "DELETE FROM Product_order WHERE order_id = %s"
                values = (form.order_id_delete.data,)
                mycursor.execute(sql, values)
                mydb.commit()
            return redirect('/product_order')

        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Product_order")
        product_order_data = mycursor.fetchall()

        return render_template('product_order.html', form=form, product_order_data=product_order_data)

    except Exception as e:
        logging.exception('Error in product_order(): ' + str(e))

#HERE
@app.route("/sale", methods=["GET", "POST"])
@login_required
@admin_required
def sale():
    form = AddDeleteForm()
    try:
        if form.validate_on_submit():
            mycursor = mydb.cursor()

        # Add/Delete sale
            if form.add_sale.data:
                sql = "INSERT INTO Sale (store_id, date, sale_id, revenue, quantity) VALUES (%s, %s, %s, %s, %s)"
                values = (form.store_id_sale.data, form.sale_date.data, form.sale_id.data, form.revenue.data, form.sale_quantity.data)
                mycursor.execute(sql, values)
                mydb.commit()
            elif form.delete_sale.data:
                sql = "DELETE FROM Sale WHERE sale_id = %s"
                values = (form.sale_id.data,)
                mycursor.execute(sql, values)
                mydb.commit()
            return redirect('/sale')

        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Sale ORDER BY sale_id")
        sale_data = mycursor.fetchall()

        return render_template('sale.html', form=form, sale_data=sale_data)

    except Exception as e:
        logging.exception('Error in sale(): ' + str(e))

#HERE

@app.route("/store_location", methods=["GET", "POST"])
@login_required
@admin_required
def store_location():
    form = AddDeleteForm()
    try:
        if form.validate_on_submit():
            mycursor = mydb.cursor()

        # Add/Delete store_location
            if form.add_store_location.data:
                sql = "INSERT INTO Store_Location (store_id, contact_info, address) VALUES (%s, %s, %s, %s)"
                values = (form.store_id.data, form.contact_info.data, form.address.data)
                mycursor.execute(sql, values)
                mydb.commit()
            elif form.delete_store_location.data:
                sql = "DELETE FROM Store_Location WHERE store_id = %s"
                values = (form.store_id.data,)
                mycursor.execute(sql, values)
                mydb.commit()
            return redirect('/store_location')

        mycursor = mydb.cursor()

        mycursor.execute("SELECT * FROM Store_Location ORDER BY store_id")
        store_location_data = mycursor.fetchall()

        return render_template('store_location.html', form=form, store_location_data=store_location_data)

    except Exception as e:
        logging.exception('Error in store_location(): ' + str(e))

#HERE
@app.route("/users", methods=["GET", "POST"])
@login_required
@admin_required
def users():
    try:
        form = AddDeleteForm()
        if form.validate_on_submit():
            mycursor = mydb.cursor()
            # Delete user
            if form.delete_user.data:
                sql = "DELETE FROM Users WHERE username = %s"
                values = (form.username.data,)
                mycursor.execute(sql, values)
                mydb.commit()
            # Make user an admin
            elif form.set_admin.data:
                #DEBUG THIS
                set_admin(form.username_set_admin.data)
            else:
                unset_admin(form.username_unset_admin.data)
            return redirect('/users')
        mycursor = mydb.cursor()

        mycursor.execute("SELECT id, username, isadmin FROM Users ORDER BY id")
        user_data = mycursor.fetchall()

        return render_template('users.html', form=form, user_data=user_data)
    except Exception as e:
        logging.exception('Error in users(): ' + str(e))
        return 'Error: ' + str(e), 500

@login_required
@admin_required
@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    return render_template('home.html') 
    
# Define a User model class
class User:
    def __init__(self, id, username, password_hash, is_admin=False):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin

# CREATE USER
def create_user(username, password):
    print("here yh")
    password_hash = generate_password_hash(password)
    cursor = mydb.cursor()
    sql = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
    values = (username, password_hash)
    cursor.execute(sql, values)
    mydb.commit()
    print("here 2")
    cursor.close()

# GET USER
def get_user(username):
    cursor = mydb.cursor()
    sql = "SELECT id, username, password_hash, isadmin FROM users WHERE username = %s"
    values = (username,)
    cursor.execute(sql, values)
    row = cursor.fetchone()
    if row:
         user = User(row[0], row[1], row[2], bool(row[3]))
    else:
        user = None
    cursor.close()
    return user


def get_user_by_id(user_id):
    cursor = mydb.cursor()
    sql = "SELECT id, username, password_hash, isadmin FROM users WHERE id = %s"
    values = (user_id,)
    cursor.execute(sql, values)
    row = cursor.fetchone()
    if row:
        user = User(row[0], row[1], row[2], bool(row[3]))
    else:
        user = None
    cursor.close()
    return user

def set_admin(username):
    cursor = mydb.cursor()
    print("username", username)
    sql = "UPDATE users SET isadmin = 1 WHERE username = %s"
    values = (username,)
    cursor.execute(sql, values)
    mydb.commit()
    cursor.close()

def unset_admin(username):
    cursor = mydb.cursor()
    sql = "UPDATE users SET isadmin = 0 WHERE username = %s"
    values = (username,)
    cursor.execute(sql, values)
    mydb.commit()
    cursor.close()

def update_user(user):
    cursor = mydb.cursor()
    sql = "UPDATE users SET username = %s, password_hash = %s WHERE id = %s"
    values = (user.username, user.password_hash, user.id)
    cursor.execute(sql, values)
    mydb.commit()
    cursor.close()

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and check_password_hash(user.password_hash, password):
            # If the password is correct, log in the user
            session['user_id'] = user.id
            session['username'] = user.username
            # Check if the user is an admin
            if user.is_admin:
                session['is_admin'] = True
                session['logged_in'] = True
                return redirect(url_for('home'))
            else:
                session['logged_in'] = True
                return redirect(url_for('customer_view'))
        else:
            # If the password is incorrect, show an error message
            flash('Invalid username or password')
            return redirect(url_for('login'))
    else:
        # If the request method is GET, show the login page
        return render_template('login.html')


@app.route('/account', methods=['GET', 'POST'])
@login_required
def update_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = session.get('user_id')
        # Use the user ID to fetch the user data
        user = get_user_by_id(user_id)
        # Update the user data
        if username != user.username:
            user.username = username
        if password:
            user.password_hash = generate_password_hash(password)
        # Save the updated user data to the database
        update_user(user)
        flash('Account updated successfully', 'success')
        return redirect(url_for('update_account'))
    else:
        user_id = session.get('user_id')
        # Use the user ID to fetch the user data
        user = get_user_by_id(user_id)
        return render_template('account.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        create_user(username, password)
        flash('Account created successfully')
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)