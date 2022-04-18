from flask import Flask, jsonify
from flask import render_template
from flask import request
from data.resourses import ApplicationResource
from data.resourses import GoodByCategory
from data.resourses import GoodsResource
from data.resourses import UserResource
from data.applications import Application
from data.users import User
from data.forms import ApplicationForm
from data.forms import LoginForm
from random import sample
from flask import session
from flask import redirect
from flask_login import current_user 
from flask_login import login_user
from flask_login import logout_user
from data.forms import RegisterForm
from werkzeug.datastructures import CombinedMultiDict
from data.forms import NewGoodForm
from flask_restful import Api
from flask_login import login_required
from flask_login import LoginManager
from werkzeug.exceptions import Unauthorized
from werkzeug.exceptions import InternalServerError
from data import db_session
from data.goods import Good
from werkzeug.utils import secure_filename
import os

from utils import load_settings 


app = Flask(__name__, template_folder='static/templates', static_folder='static')
settings = load_settings()
app.config['SECRET_KEY'] = settings['secret_key']
app.config['UPLOAD_FOLDER'] = settings['upload_directory']
api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
        )
        user.permission_level = 1
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/')
def main_view():
    dbs = db_session.create_session()
    goods = dbs.query(Good).all()
    
    goods = sample(goods, 10)

    categories = ['Метёлки', 'Бебрики', 'Пылесосы', 'Учебники английского', 'Прочий мусор']
    
    return render_template('goods.html', title='БебраМаркет', data=goods, categories=categories)


@app.route('/<category>')
def category_view(category):
    dbs = db_session.create_session()
    goods = dbs.query(Good).filter(Good.category == category).all()

    categories = ['Метёлки', 'Бебрики', 'Пылесосы', 'Учебники английского', 'Прочий мусор']
    
    return render_template('goods.html', title='О.Магазин!', data=goods, categories=categories)


@app.route('/add_to_cart/<ident>', methods=['POST'])
def add_to_cart_view(ident):
    if session.get('cart', False):
        if session['cart'].get(ident, False):
            session['cart'][ident] += 1
        else:
            session['cart'][ident] = 1

        session.modified = True
    else:
        session['cart'] = {ident: 1}

    return redirect('/')


@app.route('/cart', methods=['POST', 'GET'])
def cart_view():
    if request.method == 'POST':
        return redirect('/')

    dbs = db_session.create_session()
    
    goods = list()
    if not session.get('cart', False):
        session['cart'] = dict()

    for item in session['cart']:
        goods.append([dbs.query(Good).filter(Good.id == item).one_or_none(),  session['cart'][item]])
    
    total = sum([good[0].price * good[1] for good in goods])

    goods = [goods[i:i + 3] for i in range(0, len(goods), 3)]
    return render_template('cart.html', cart=goods, total=total)


@app.route('/clear-cart')
def clear_cart_veiw():
    if session['cart']:
        session['cart'] = dict()
    else:
        pass
    
    return redirect('/cart')


@app.route('/add_goods', methods=['GET', 'POST'])
@login_required
def add_good_view():
    if current_user.permission_level != 9:
        return render_template('404.html')

    form = NewGoodForm(CombinedMultiDict((request.files, request.form)))

    if form.validate_on_submit():
        dbs = db_session.create_session()
        
        item = Good()
        item.article = form.article.data
        item.about = form.about.data
        item.count = form.count.data
        item.price = form.price.data
        item.category = form.category.data
                
        dbs.add(item)
        dbs.commit()

        new_item = dbs.query(Good).filter(Good.article == item.article).one_or_none()

        if new_item is None:
            print('Critical error: cannot save new article')
            return redirect('/error/404')

        try:
            f = form.image.data
            fn = secure_filename(f"{new_item.id}.jpg")
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
        except OSError:
            print('Не удалось сохранить картинку при создании товара.')
            return redirect('/cannot_save_image/creation')
            
        return redirect('/')
    
    return render_template('add_good.html', form=form)


@app.route('/all_applications')
@login_required
def all_applications_view():
    if current_user.permission_level != 9:
        return redirect('/')

    dbs = db_session.create_session()
    
    applications = dbs.query(Application).all()

    return render_template('all_applications.html', applications=applications)


@app.route('/application', methods=['POST', 'GET'])
@login_required
def application_view():
    form = ApplicationForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        application = Application()
        application.name = name
        application.email = email
        application.message = message

        dbs = db_session.create_session()
        dbs.add(application)
        dbs.commit()

        return redirect('/')

    return render_template('applications.html', form=form)


@app.errorhandler(404)
def error404_handler(error):
    return render_template('404.html')


@app.errorhandler(Unauthorized)
def error401_handler(error):
    print(f"""\n!!! Попытка получения несанкционированного доступа !!!
                IP Адрес: {request.remote_addr}
                Schema: {request.scheme}
           """)

    return render_template('404.html')


@app.errorhandler(InternalServerError)
def internal_error_handler(error):
    print('Внимание !!! Внутренняя ошибка сервера !!!')
    print(f'Сообщение получено от {request.scheme}')

    return render_template('404.html')


api.add_resource(GoodsResource, '/api/v2/get/goods/by_id/<int:id>')
api.add_resource(GoodByCategory, '/api/v2/get/goods/by_category/<category>')
api.add_resource(ApplicationResource, '/api/v2/get/application/by_id/<int:id>') 
api.add_resource(UserResource, '/api/v2/get/user/<criterion>')

db_session.global_init("db/ad.db")

app.run(port=settings['port'], debug=settings['debug'])
