from data.users import User
from . import db_session
from .goods import Good
from flask import jsonify
from flask_restful import Resource
from .applications import Application


class GoodsResource(Resource):
    def get(self, id): 
        dbs = db_session.create_session()
        good = dbs.query(Good).get(id)

        return jsonify({'success': good.as_dict()})

    def post(self, article, about, price, count, category):
        dbs = db_session.create_session()

        good = Good()
        good.article = article
        good.about = about
        good.price = price
        good.count = count
        good.category = category
        
        dbs.add(good)
        
        return jsonify({'success': 200})


class ApplicationResource(Resource):
    def get(self, id):
        dbs = db_session.create_session()
        application = dbs.query(Application).get(id)

        return jsonify({'success': application.as_dict()})


class UserResource(Resource):
    def get(self, criterion):
        dbs = db_session.create_session()

        try:
            criterion = int(criterion)
            cr_type = 'id'
        except:
            cr_type = 'email'

        if cr_type == 'id':
            user = dbs.query(User).filter(User.id == criterion).one_or_none()
        elif cr_type == 'email':
            user = dbs.query(User).filter(User.email == criterion).one_or_none()
        else:
            user = None

        return user


class GoodByCategory(Resource):
    def get(self, category):
        dbs = db_session.create_session()

        goods = dbs.query(Good).filter(Good.category == category).all()

        return goods
