import werkzeug
import os
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.secret_key = os.urandom(24)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


# CREATED TABLE IN DB
class User(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email_ = request.form.get("email")
        unhashed_p = request.form.get("password")
        password_ = werkzeug.security.generate_password_hash(unhashed_p, method='pbkdf2:sha256', salt_length=8)
        name_ = request.form.get("name")
        registered_user = User(email=email_, password=password_, name=name_)
        db.session.add(registered_user)
        db.session.commit()
        print("committed")
        return render_template("secrets.html", name=request.form.get('name'))
    return render_template("register.html")


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/login', methods=["POST", "GET"])
def login():
    form = User()
    if form.validate_on_submit():
        login_user(User.user)
        flash("Logged in successfully")
        return redirect(url_for("secrets", name=form.name))
    return render_template("login.html", form=form)


@app.route('/secrets', methods=["POST", "GET"])
def secrets():
    all_users = User.query.all()
    return render_template("secrets.html", users=all_users)


@app.route('/logout')
def logout():
    pass


@app.route('/download', methods=["GET"])
def download():
    return send_from_directory(directory="static", path="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
