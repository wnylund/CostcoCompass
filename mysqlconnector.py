import mysql.connector
from flask import Flask, request, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config['SECRET_KEY'] = 'williscool'


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
    # Fields for Product table
    product_id = StringField('Product ID')
    category_id_2 = StringField('Category ID')
    name = StringField('Name')
    description = StringField('Description')
    price = StringField('Price')

    # Submit buttons
    add_category = SubmitField('Add Category')
    delete_category = SubmitField('Delete Category')

    add_product = SubmitField('Add Product')
    delete_product = SubmitField('Delete Product')



@app.route("/", methods=["GET", "POST"])
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

        # Add/Delete logic for other tables (e.g., Customer, Employee, Inventory)

        return redirect('/')

    # Fetch data for all tables
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM Category")
    category_data = mycursor.fetchall()

    mycursor.execute("SELECT * FROM Product")
    product_data = mycursor.fetchall()

    # Fetch data for other tables (e.g., Customer, Employee, Inventory)
    return render_template('home.html', form=form, category_data=category_data, product_data=product_data) # Pass other table data to the template



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)