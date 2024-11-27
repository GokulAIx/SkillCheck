# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Initialize db object here

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(50))
    topic = db.Column(db.String(50))
    question = db.Column(db.String(200))
    options = db.Column(db.PickleType)  # Assuming options are stored as a list
    correct_option = db.Column(db.String(10))  # This should match the keyword you are passing

    def __init__(self, domain, topic, question, options, correct_option):
        self.domain = domain
        self.topic = topic
        self.question = question
        self.options = options
        self.correct_option = correct_option
