from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user, LoginManager
from sqlalchemy.orm import relationship
from forms import RegisterForm, LoginForm, AddForm
import datetime
import os

app = Flask(__name__)

bootstrap = Bootstrap5(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    lists = relationship("List", back_populates="user")


class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    due_date = db.Column(db.String(150), nullable=True)
    user = relationship("User", back_populates="lists")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_todos = List.query.all()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html", todos=all_todos)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        password = form.passwords.data
        user.password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.passwords.data
        user = User.query.filter_by(email=email).first()
        if not user:
            error = "This email doesnt exist. Please try again."
            return render_template("login.html", error=error, form=form)
        elif not check_password_hash(user.password, password):
            error = "Password incorrect. Please try again."
            return render_template("login.html", error=error, form=form)
        else:
            login_user(user)
            return redirect("/")
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add_todo', methods=["GET", "POST"])
@login_required
def add():
    form = AddForm()
    if form.validate_on_submit():
        todo = List()
        todo.name = form.name.data
        todo.due_date = form.due_date.data
        todo.user_id = current_user.id
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=form)


@app.route('/delete/<int:to_id>')
@login_required
def delete(to_id):
    todo_delete = List.query.get(to_id)
    db.session.delete(todo_delete)
    db.session.commit()
    return redirect(url_for('home'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True)
