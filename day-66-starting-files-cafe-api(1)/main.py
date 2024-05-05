from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from random import choice
'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
    
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random", methods=["GET"])
def random():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = choice(all_cafes)
    
    ## This can also be used but the better way is to do it is calling the inner functions 
    # maps_json= {}
    # maps_json["maps"] = { "can_take_calls" : random_cafe.can_take_calls, "coffee_price" : random_cafe.coffee_price, "has_sockets" : random_cafe.has_sockets, 
    #         "has_toilet" : random_cafe.has_toilet, "has_wifi" : random_cafe.has_toilet, "id" : random_cafe.id, "img_url" : random_cafe.img_url, 
    #         "location" : random_cafe.location, "map_url" : random_cafe.map_url, "name" : random_cafe.name, "seats" : random_cafe.seats }
    return jsonify(random_cafe.to_dict())
    
    
@app.route("/all", methods=["GET"])
def all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    cafes_data = [row.to_dict() for row in result]
    return jsonify(cafes_data)
    
@app.route("/search/", methods=["GET"])
def search_cafes():
    query_location = request.args.get("loc")
    ## If location found 
    ## Serach in the database 
    get_location = Cafe.query.filter_by(location=query_location).first()
    if get_location is not None:
        return jsonify(get_location.to_dict())
    else:
    ## If location not found 
        return jsonify( {"error" : {"Not Found" : "Sorry, we don't have a cafe at that location."}} )
    
if __name__ == '__main__':
    app.run(debug=True)
