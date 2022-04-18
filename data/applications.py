import sqlalchemy
from .db_session import SqlAlchemyBase


class Application(SqlAlchemyBase):
    __tablename__ = 'applications'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String)
    
    email = sqlalchemy.Column(sqlalchemy.String)

    message = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f"""Author: {self.name}
                   Email: {self.email}
                   Message: {self.message}
                """
    
    def as_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'message': self.message
        }
