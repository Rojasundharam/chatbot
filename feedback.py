# feedback.py

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    query = Column(String)
    response = Column(String)
    rating = Column(Float)

engine = create_engine('sqlite:///feedback.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def save_feedback(query, response, rating):
    session = Session()
    feedback = Feedback(query=query, response=response, rating=rating)
    session.add(feedback)
    session.commit()
    session.close()