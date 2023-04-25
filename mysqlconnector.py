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
    # Fields for Category table
    category_id = StringField('Category ID')
    category_name = StringField('Category Name')

    #Product 
    product_id = StringField('Product ID')
    category_id_2 = StringField('Category ID')
    name = StringField('Name')
    description = StringField('Description')
    price = StringField('Price')

    #Inventory
    product_id_inventory = StringField('Product ID')
    quantity = StringField('Quantity')
    store_id_inventory = StringField('Store ID')

    #Customer (customer_id, email, name, join_date) #HERE

    #Employee (position, email, name, employee_id) #HERE

    #Product_order (customer_id, order_id, item, status, order_date) #HERE

    #Sale (store_id, date, sale_id, revenue, quantity) #HERE

    #Store_Location (Inventory_id, store_id, contact_info, address) #HERE

    #User (id, username, isadmin) #HERE
    user_id = StringField('User ID')
    username = StringField('username')
    is_admin = StringField('Is Admin')

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

@app.route('/')
def index():
    return redirect(url_for('login'))

#EXAMPLE
@app.route("/category", methods=["GET", "POST"])
@login_required
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
                sql = "DELETE FROM Category WHERE category_id = %s"
                values = (form.category_id.data,)
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
    
#EXAMPLE
@app.route("/inventory", methods=["GET", "POST"])
@login_required
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
                print("in delete")
                sql = "DELETE FROM Inventory WHERE product_id = %s"
                values = (form.product_id_inventory.data,)
                print("values: ", values)
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
    
@app.route("/product", methods=["GET", "POST"])
@login_required
def product():
    try:
        form = AddDeleteForm()
        if form.validate_on_submit():
            mycursor = mydb.cursor()
            # Add/Delete Product
            if form.add_product.data:
                print("in add here")
                sql = "INSERT INTO Product (product_id, category_id, name, description, price) VALUES (%s, %s, %s, %s, %s)"
                values = (form.product_id.data, form.category_id_2.data, form.name.data, form.description.data, form.price.data)
                mycursor.execute(sql, values)
                mydb.commit()
            elif form.delete_product.data:
                print("in delete here")
                sql = "DELETE FROM Product WHERE product_id = %s"
                values = (form.product_id.data,)
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
def customer():
    form = AddDeleteForm()
    if form.validate_on_submit():
        mycursor = mydb.cursor()

#HERE
@app.route("/employee", methods=["GET", "POST"])
@login_required
def employee():
    form = AddDeleteForm()
    if form.validate_on_submit():
        mycursor = mydb.cursor()

#HERE
@app.route("/product_order", methods=["GET", "POST"])
@login_required
def product_order():
    form = AddDeleteForm()
    if form.validate_on_submit():
        mycursor = mydb.cursor()

#HERE
@app.route("/sale", methods=["GET", "POST"])
@login_required
def sale():
    form = AddDeleteForm()
    if form.validate_on_submit():
        mycursor = mydb.cursor()

#HERE
@app.route("/store_location", methods=["GET", "POST"])
@login_required
def store_location():
    form = AddDeleteForm()
    if form.validate_on_submit():
        mycursor = mydb.cursor()

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
            return redirect('/users')
        mycursor = mydb.cursor()

        mycursor.execute("SELECT id, username, isadmin FROM Users ORDER BY id")
        user_data = mycursor.fetchall()

        return render_template('users.html', form=form, user_data=user_data)
    except Exception as e:
        logging.exception('Error in users(): ' + str(e))
        return 'Error: ' + str(e), 500


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    print(session.get('admin'))
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
    password_hash = generate_password_hash(password)
    cursor = mydb.cursor()
    sql = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
    values = (username, password_hash)
    cursor.execute(sql, values)
    mydb.commit()
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

def set_admin(user):
    cursor = mydb.cursor()
    user.is_admin = True
    sql = "UPDATE users SET isadmin = %s WHERE id = %s"
    values = (user.is_admin, user.id)
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
        print("is admin?: ", user.is_admin)
        if user and check_password_hash(user.password_hash, password):
            # If the password is correct, log in the user
            session['user_id'] = user.id
            session['username'] = user.username
            # Check if the user is an admin
            if user.is_admin:
                print("GOT HERE HECK YEAH")
                session['is_admin'] = True
            session['logged_in'] = True
            return redirect(url_for('home'))
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