from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateTimeLocalField, DateTimeField
from wtforms.validators import DataRequired, Email


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    passwords = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Done")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    passwords = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AddForm(FlaskForm):
    name = StringField("Name of To-Do", validators=[DataRequired()])
    due_date = DateTimeField("Expiration Date (year-month-day hour:minute)", format='%Y-%m-%d %H:%M:%S',
                             validators=None)
    submit = SubmitField("Submit")
