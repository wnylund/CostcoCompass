import mysql.connector
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config['SECRET_KEY'] = 'williscool'
bcrypt = Bcrypt(app)

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="test",
  database="costco"
)

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


    # Submit buttons
    add_category = SubmitField('Add Category')
    delete_category = SubmitField('Delete Category')

    add_product = SubmitField('Add Product')
    delete_product = SubmitField('Delete Product')

    add_inventory = SubmitField('Add Inventory')
    delete_inventory = SubmitField('Delete Inventory')

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route("/home", methods=["GET", "POST"])
def home():
    form = AddDeleteForm()
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

        # Add/Delete Inventory
        if form.add_inventory.data:
            sql = "INSERT INTO Inventory (product_id, quantity, store_id) VALUES (%s, %s)"
            values = (form.product_id_inventory.data, form.quantity.data, form.store_id_inventory.data)
            mycursor.execute(sql, values)
            mydb.commit()
        elif form.delete_category.data:
            sql = "DELETE FROM Inventory WHERE category_id = %s"
            values = (form.product_id.data)
            mycursor.execute(sql, values)
            mydb.commit()

        # Add/Delete logic for other tables (e.g., Customer, Employee, Inventory)

        return redirect('/')

    # Fetch data for all tables
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM Category")
    category_data = mycursor.fetchall()

    mycursor.execute("SELECT * FROM Product")
    product_data = mycursor.fetchall()

    mycursor.execute("SELECT * FROM Inventory")
    inventory_data = mycursor.fetchall()

    # Fetch data for other tables (e.g., Customer, Employee, Inventory)
    return render_template('home.html', form=form, category_data=category_data, product_data=product_data, inventory_data=inventory_data) # Pass other table data to the template

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
    sql = "SELECT id, username, password_hash FROM users WHERE username = %s"
    values = (username,)
    cursor.execute(sql, values)
    row = cursor.fetchone()
    if row:
        user = User(row[0], row[1], row[2])
    else:
        user = None
    cursor.close()
    return user

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and check_password_hash(user.password_hash, password):
            # If the password is correct, log in the user
            # Check if the user is an admin
            if user.is_admin:
                session['is_admin'] = True
            return redirect(url_for('home'))
        else:
            # If the password is incorrect, show an error message
            flash('Invalid username or password')
            return redirect(url_for('login'))
    else:
        # If the request method is GET, show the login page
        return render_template('login.html')

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