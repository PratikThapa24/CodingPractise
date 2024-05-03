from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Column

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"
db = SQLAlchemy(app)

##CREATE TABLE
class Book(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=True, nullable=False)
    author = Column(String(250), nullable=False)
    rating = Column(Float, nullable=False)

    def __repr__(self):
        return f'<Book {self.title}>'


@app.route('/')
def home():
    all_books = Book.query.all()
    return render_template("index.html", books = all_books)

@app.route("/add", methods = ['POST', 'GET'])
def add():
    if request.method == 'POST':
        new_book = Book(title=request.form['title'], author=request.form['author'], rating=request.form['rating']) 
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template("add.html")

@app.route("/edit/<int:index>", methods=['POST', 'GET'])
def edit(index):
    
    if request.method == "POST":
        book = Book.query.get(index)
        book.rating = request.form['new_rating']
        db.session.commit()
        return redirect(url_for('home'))
    book = Book.query.get(index)
    return render_template("edit.html", book = book)
    
@app.route("/delete/<int:index>", methods=['POST', 'GET'])
def delete(index):
    book = Book.query.get(index)
    if book:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

