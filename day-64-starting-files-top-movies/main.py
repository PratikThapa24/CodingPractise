from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Column
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests
import os 
'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
## Accessing the enviroment variable and requesting api from The Movie Data Base 
movie_api_key = os.environ.get("MOVIEPASS")
url = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"
MOVIE_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
# CREATE DB
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-movies-collections.db'

db = SQLAlchemy(model_class=Base)
db.init_app(app)

## Creating a flask form for editing the movie
class MovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10. eg 9.3", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")

## Creating a flask form for adding a new movie
class NewMovie(FlaskForm):
    title = StringField("Movie Title")
    submit = SubmitField("Add Movie")
    
class Movie(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    year = Column(Integer)
    description = Column(String)
    rating = Column(Float)
    ranking = Column(Integer)
    review = Column(String)
    img_url = Column(String)   

with app.app_context():
    db.create_all()
    
## After adding the new_movie the code needs to be commented out/deleted.
## So you are not trying to add the same movie twice. The db will reject non-unique movie titles.
# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )
# with app.app_context():
#     db.session.add(second_movie)
#     db.session.commit()
    

@app.route("/")
def home():
    all_movie = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()
    for i in range(len(all_movie), 1):
        all_movie[i].ranking = len(all_movie) - i
    db.session.commit()
    return render_template("index.html", movies = all_movie)

@app.route("/edit/<int:index>", methods=['POST', 'GET'])
def edit(index):
    form = MovieForm()
    get_movie = Movie.query.get(index)
    if form.validate_on_submit():
        get_movie.rating = float(form.rating.data)
        get_movie.review = form.review.data    
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template("edit.html", movie=get_movie, form = form)

@app.route("/delete/<int:index>", methods=['POST', 'GET'])
def delete(index):
    get_movie = Movie.query.get(index)
    if get_movie:
        db.session.delete(get_movie)
        db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=['POST', 'GET'])
def add():
    form = NewMovie()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(url, params={"api_key": movie_api_key, "query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", options=data)
    
    return render_template("add.html", form=form)

@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_url = f"{MOVIE_URL}/{movie_api_id}?api_key={movie_api_key}"
        response = requests.get(movie_url, params={"api_key": movie_api_key, "language": "en-US"})
        data = response.json()
        print(data)
        new_movie = Movie(title=data["title"],
                year=data["release_date"].split("-")[0],
                img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
                description=data["overview"]
            )
        db.session.add(new_movie)
        db.session.commit()
        
        return redirect(url_for('edit', index=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
