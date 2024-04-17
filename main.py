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


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATED TABLE IN DB
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        email_ = request.form.get("email")
        unhashed_p = request.form.get("password")
        password_ = werkzeug.security.generate_password_hash(unhashed_p, method='pbkdf2:sha256', salt_length=8)
        name_ = request.form.get("name")
        existing_user = User.query.filter_by(email=email_).first()
        if existing_user:
            flash("You are already registered, log in instead.")
        else:
            registered_user = User(email=email_, password=password_, name=name_)
            db.session.add(registered_user)
            db.session.commit()
        return render_template("secrets.html", name=request.form.get('name'))
    return render_template("register.html", logged_in = current_user.is_authenticated, name=request.form.get('name'))


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email_ = request.form.get("email")
        unhashed_p = request.form.get("password")
        user = User.query.filter_by(email=email_).first()
        check_p = werkzeug.security.check_password_hash(user.password, unhashed_p)
        if not user or not check_p:
            flash("Invalid credentials, please try again.")
        if user and check_p:
            login_user(user)
            flash("Logged in successfully")
            return redirect(url_for("secrets", name=User.name))
    return render_template("login.html", logged_in = current_user.is_authenticated)


@app.route('/secrets', methods=["POST", "GET"])
@login_required
def secrets():
    all_users = User.query.all()
    return render_template("secrets.html", users=all_users, name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/download', methods=["GET"])
@login_required
def download():
    return send_from_directory(directory="static", path="files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
