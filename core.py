from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from sqlalchemy import func
from data.applications import Application
from data.users import User
from data.forms import ApplicationForm
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
# TODO: Сделать кнопку случайного товара
# TODO: Довести до ума корзину
# TODO: Реализовать алгоритм работы промокодов
# TODO: Оптимизировать файл requirements.txt


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
    goods = dbs.query(Good).all()
    
    categories = [[] for _ in range(5)]

    format_categories(goods, categories)
    max_len = max(len(x) for x in categories)
    
    rows = [['Метёлки', 'Бебрики', 'Пылесосы', 'Учебники английского', 'Прочий мусор']]

    for i in range(max_len):
        item1 = categories[0][i] if len(categories[0]) > i else ''
        item2 = categories[1][i] if len(categories[1]) > i else ''
        item3 = categories[2][i] if len(categories[2]) > i else ''
        item4 = categories[3][i] if len(categories[3]) > i else ''
        item5 = categories[4][i] if len(categories[4]) > i else ''
        rows.append([item1, item2, item3, item4, item5])

    return render_template('goods.html', title='О.Магазин!', data=rows, max_item_count=range(max_len))


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


@app.route('/cart')
def cart_view():
    dbs = db_session.create_session()
    
    goods = list()
    if not session.get('cart', False):
        session['cart'] = dict()
    for item in session['cart']:
        goods.append([dbs.query(Good).filter(Good.id == item).one_or_none(),  session['cart'][item]])

    goods = [goods[i:i + 3] for i in range(0, len(goods), 3)]

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
@login_required
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
        item.category = form.category.data
                
        dbs.add(item)
        dbs.commit()

        new_item = dbs.query(Good).filter(Good.article == item.article).one()

        f = form.image.data
        fn = secure_filename(f"{new_item.id}.jpg")
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))


        return redirect('/')
    
    return render_template('add_good.html', form=form)


@app.route('/application', methods=['POST', 'GET'])
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


def format_categories(goods, categories):
    for good in goods:
        if good.category == 'Метёлки':
            categories[0].append(good)
        elif good.category == 'Бебрики':
            categories[1].append(good)
        elif good.category == 'Пылесосы':
            categories[2].append(good)
        elif good.category == 'Учебники английского':
            categories[3].append(good)
        else:
            categories[4].append(good)


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
    good1.count = 50
    good1.category = 'Метёлки'

    good2 = Good()
    good2.article = 'Швабра'
    good2.about = 'Не является пылесосом'
    good2.price = 500.00
    good2.count = 50
    good2.category = 'Метёлки'

    dbs.add(good1)
    dbs.add(good2)

    good1 = Good()
    good1.article = 'Пылесос Miele'
    good1.about = 'Отлично подойдёт для дачи или загородного дома, прекрасно чистит пол (наверное)'
    good1.price = 4000.00
    good1.count = 50
    good1.category = 'Пылесосы'

    good2 = Good()
    good2.article = 'Промышленный пылесос Mekqodnwn x5 super ultra'
    good2.about = 'Нечего говорить, лучше сразу покупать'
    good2.price = 17990.00
    good2.count = 50
    good2.category = 'Пылесосы'

    dbs.add(good1)
    dbs.add(good2)

    good1 = Good()
    good1.article = 'Правдивый пылесос Никитос'
    good1.about = 'Скажет вам правду в любой момент.  *Иногда не хочет пылесосить'
    good1.price = 100.00
    good1.count = 50
    good1.category = 'Пылесосы'

    good2 = Good()
    good2.article = 'Робот-пылесос Xiaomi mega ultra'
    good2.about = 'Пылесосит даже то, что не надо. Супер вещь'
    good2.price = 19990.00
    good2.count = 50
    good2.category = 'Пылесосы'

    dbs.add(good1)
    dbs.add(good2)

    good1 = Good()
    good1.article = 'Робот-пылесос Samsung amK'
    good1.about = 'Идеально подходит для сильных загрязнений, может катать котов'
    good1.price = 7800.00
    good1.count = 50
    good1.category = 'Пылесосы'

    good2 = Good()
    good2.article = 'Водонапорная станция города Бебра'
    good2.about = 'Хотите наполнить ванну за 0,7 секунд? Долго моете полы? Хотите наполнить 27 чайников за считанные секунды? Водонапорная башня вам очень поможет.'
    good2.price = 27000000.00
    good2.count = 50
    good2.category = 'Бебрики'

    dbs.add(good1)
    dbs.add(good2)

    good1 = Good()
    good1.article = 'Герб города Бебра'
    good1.about = 'Всегда мечтали официально владеть гербом самого лучшего города мира? Мы нашли решение'
    good1.price = 300.00
    good1.count = 50
    good1.category = 'Бебрики'

    good2 = Good()
    good2.article = 'Краткая характеристика Бебры'
    good2.about = '270 страниц с кратким описанием'
    good2.price = 56000.00
    good2.count = 50
    good2.category = 'Бебрики'

    dbs.add(good1)
    dbs.add(good2)

    dbs.commit()

    good1 = Good()
    good1.article = 'Самоучитель английского языка'
    good1.about = ''
    good1.price = 300.00
    good1.count = 50
    good1.category = 'Учебники английского'

    good2 = Good()
    good2.article = 'Учебник английского 9 класс, Афанасьева, Михеева.jpg'
    good2.about = ''
    good2.price = 400.00
    good2.count = 50
    good2.category = 'Учебники английского'

    dbs.add(good1)
    dbs.add(good2)

    good2 = Good()
    good2.article = 'Учебник Spotlight 9 класс.  Students Book.jpg'
    good2.about = ''
    good2.price = 450.00
    good2.count = 50
    good2.category = 'Учебники английского'

    dbs.add(good1)
    dbs.add(good2)

    dbs.commit()
else:
    #if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
