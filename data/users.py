import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)

    email = sqlalchemy.Column(sqlalchemy.String, 
                              index=True, unique=True, nullable=True)

    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    permission_level = sqlalchemy.Column(sqlalchemy.Integer)
                                    
    def __repr__(self):
        return f'Пользователь "{self.name}", почта -- {self.email}'

    def check_password(self, password):
        if password == self.hashed_password:
            return True
        else:
            return False

    def set_password(self, password):
        self.hashed_password = password
