from flask import Flask
from flask import render_template
from data import db_session
from data.goods import Good


app = Flask(__name__, template_folder='static/templates', static_folder='static')
app.config['SECRET_KEY'] = 'kjnc{On3[ijnP3[oNCQ@(nC#('


@app.route('/')
def main_view():
    return render_template('goods.html', title='О.Магазин!')


@app.route('/goods')
def test_view():
    dbs = db_session.create_session()
    goods = [good.__repr__() for good in dbs.query(Good).all()]
    goods = [', '.join(good) for good in goods]

    return '<br>'.join(goods)


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
