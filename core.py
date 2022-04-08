from flask import Flask, jsonify
from flask import render_template
from flask import session
from data.users import User
from data.forms import LoginForm
from flask import redirect
from flask_login import login_user
from flask_login import logout_user
from data.forms import RegisterForm
from flask_restful import reqparse
from flask_restful import abort
from flask_restful import Api
from flask_restful import Resource
from flask_login import login_required
from flask_login import LoginManager
from data import db_session
from data.goods import Good


app = Flask(__name__, template_folder='static/templates', static_folder='static')
app.config['SECRET_KEY'] = 'kjnc{On3[ijnP3[oNCQ@(nC#('
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
    return render_template('goods.html', title='О.Магазин!')


@app.route('/goods')
def test_view():
    dbs = db_session.create_session()
    goods = [good.__repr__() for good in dbs.query(Good).all()]
    goods = [', '.join(good) for good in goods]

    return '<br>'.join(goods)


class GoodsResource(Resource):
    def get(self, id): 
        dbs = db_session.create_session()
        good = dbs.query(Good).get(id)

        return jsonify({'success': good.as_dict()})


api.add_resource(GoodsResource, '/api/v2/get_goods/by_id/<int:id>') 


db_session.global_init("db/core_db.db")

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
    app.run(debug=True)
