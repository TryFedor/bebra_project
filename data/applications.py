import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Application(SqlAlchemyBase):
    __tablename__ = 'applications'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String)
    
    email = sqlalchemy.Column(sqlalchemy.String)

    message = sqlalchemy.Column(sqlalchemy.String)
