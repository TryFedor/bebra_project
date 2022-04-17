from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms import PasswordField
from wtforms import BooleanField
from wtforms import SubmitField
from wtforms import StringField
from wtforms import DecimalField
from wtforms import IntegerField
from wtforms import FileField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired
from wtforms import FileField


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')

    submit = SubmitField('Готово')



class RegisterForm(FlaskForm):
    email = EmailField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired()])

    submit = SubmitField('Готово')


class NewGoodForm(FlaskForm):
    article = StringField('Название', validators=[DataRequired()])
    about = StringField('Описание', validators=[DataRequired()])
    price = DecimalField('Цена', validators=[DataRequired()])
    count = IntegerField('Количество', validators=[DataRequired()])
    category = StringField('Категория', validators=[DataRequired()])
    image = FileField('Картинка', validators=[FileRequired()])
    
    submit = SubmitField('Submit')


class ApplicationForm(FlaskForm):
    name = StringField('Имя')
    email = EmailField('Email')
    message = TextAreaField('Текст предложения')

    submit = SubmitField('Отправить')
