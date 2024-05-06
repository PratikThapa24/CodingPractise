from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import subprocess 


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

## Login Manager config 
login_manager = LoginManager()
login_manager.init_app(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
        
 
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

@app.route('/')
def home():
    return render_template("index.html", logged_in = current_user.is_authenticated)


@app.route('/register', methods=["POST", "GET"])
def register():
    ''' Used to register new user by hashing the user password '''
    if request.method == "POST":
        ## Check if the email is already in use 
        email = request.form['email']
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash("You've already signed up with that email, log in instead", 'error')
            return redirect(url_for('login'))
        
        ## Hash the password first 
        hashed_pass = generate_password_hash(password = request.form['password'], method='pbkdf2:sha256', salt_length = 8)
        user = User(email = request.form['email'], password = hashed_pass, name = request.form['name'])
        db.session.add(user)
        db.session.commit()
        return render_template("secrets.html", name = request.form['name'])
    return render_template("register.html", logged_in = current_user.is_authenticated)


@app.route('/login', methods = ["POST", "GET"])
def login():

    if request.method == "POST":
        ## Get the user from the database
        email = request.form['email']
        password = request.form['password']
        
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        
        if user:
            ## Check the password 
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Successfully logged in', 'success')
                return redirect(url_for('secrets'))
            else:
                flash('Password incorrect, please try again', 'error')
        else:
            flash('The email does not exist, please try again later', 'error')
            
    return render_template("login.html", logged_in = current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html", name = current_user.name, logged_in = True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
@login_required
def download():
    return send_from_directory(directory = "static", path = "files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
