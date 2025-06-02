from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class UserClassSQLAlchemy(Base):
    __tablename__ = "UsersTable"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    email = Column(String)
    birthday = Column(Date)
    userID = Column(String)
    usePassword = Column(String)