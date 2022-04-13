from flask import Flask, jsonify
from flask import render_template
from flask import request
from data.users import User
from data.forms import LoginForm
from flask import session
from flask import redirect
from flask_login import login_user
from flask_login import logout_user
from data.forms import RegisterForm
from flask import request
from werkzeug.datastructures import CombinedMultiDict
from data.forms import NewGoodForm
from flask_restful import Api
from flask_restful import Resource
from flask_login import login_required
from flask_login import LoginManager
from data import db_session
from data.goods import Good
from werkzeug.utils import secure_filename
import os 


# TODO: поместить кнопки логина и регистрации справа
# TODO: На главной странице создать разделы 
# TODO: Сделать форму для Предложений
# TODO: Сделать кнопку случайного товара
# TODO: Довести до ума корзину
# TODO: Реализовать алгоритм работы промокодов
# TODO: Оптимизировать файл requirements.txt
# TODO: Поставить логотип


app = Flask(__name__, template_folder='static/templates', static_folder='static')
app.config['SECRET_KEY'] = 'kjnc{On3[ijnP3[oNCQ@(nC#('
app.config['UPLOAD_FOLDER'] = 'static/img'
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
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.route('/')
def main_view():
    dbs = db_session.create_session()
    goods = [good for good in dbs.query(Good).all()][:9]
    goods = [goods[0], goods[1], goods[2]], [goods[3], goods[4], goods[5]], [goods[6], goods[7], goods[8]]

    return render_template('goods.html', title='О.Магазин!', data=goods)


@app.route('/add_to_cart/<ident>')
def add_to_cart_view(ident):
    if session['cart']:
        if session['cart'].get(ident, False):
            session['cart'][ident] += 1
        else:
            session['cart'][ident] = 1

        session.modified = True
    else:
        session['cart'] = {ident: 1}

    return redirect('/')


@app.route('/cart')
def cart_view():
    dbs = db_session.create_session()
    
    goods = list()
    for item in session['cart']:
        goods.append([dbs.query(Good).filter(Good.id == item).one_or_none(), session['cart'][item]])

    return render_template('cart.html', cart=goods)


@app.route('/clear-cart')
def clear_cart_veiw():
    if session['cart']:
        session['cart'] = dict()
    else:
        pass
    
    return redirect('/cart')


@app.route('/goods')
def test_view():
    dbs = db_session.create_session()
    goods = [good.__repr__() for good in dbs.query(Good).all()]
    goods = [', '.join(good) for good in goods]

    return '<br>'.join(goods)


@app.route('/add_goods', methods=['GET', 'POST'])
def add_good_view():
    form = NewGoodForm(CombinedMultiDict((request.files, request.form)))

    if form.validate_on_submit():
        dbs = db_session.create_session()
        
        item = Good()
        item.article = form.article.data
        print(item.article)
        item.about = form.about.data
        item.count = form.count.data
        item.price = form.price.data
        
        f = form.image.data
        fn = secure_filename(f"{item.article}.jpg")
        print(fn)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
        
        dbs.add(item)
        dbs.commit()

        return redirect('/')
    
    return render_template('add_good.html', form=form)


class GoodsResource(Resource):
    def get(self, id): 
        dbs = db_session.create_session()
        good = dbs.query(Good).get(id)

        return jsonify({'success': good.as_dict()})


api.add_resource(GoodsResource, '/api/v2/get_goods/by_id/<int:id>') 


db_session.global_init("db/ad.db")

if False:
    dbs = db_session.create_session()
    good1 = Good()
    good1.article = 'Метла'
    good1.about = 'Хуже чем пылесос'
    good1.price = 49.00

    dbs.add(good1)

    good2 = Good()
    good2.article = 'Швабра'
    good2.about = 'Не является пылесосом'
    good2.price = 500.00

    dbs.add(good2)

    dbs.commit()
else:
    app.run(debug=True, port=5000)
