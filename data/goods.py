import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Good(SqlAlchemyBase):
    __tablename__ = 'goods'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    article = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    
    def __repr__(self):
        return ', '.join((str(self.article), str(self.about), str(self.price)))
    
    def as_dict(self):
        return {
            'id': self.id,
            'article': self.article,
            'about': self.about,
            'price': self.price,
            'count': self.count
        }