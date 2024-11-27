# check.py
from app import app, db  # Import the app and db from app.py
from models import QuizQuestion  # Import the QuizQuestion model from models.py

with app.app_context():
    # Add some questions
    ai_questions = [
        QuizQuestion(domain="AI", topic="Coding", question="What is the primary difference between supervised and unsupervised learning?", options=["A) Supervised learning uses labeled data, while unsupervised learning does not.", "B) Supervised learning is slower than unsupervised learning.", "C) Unsupervised learning uses labeled data, while supervised learning does not.", "D) There is no difference."], correct_option="A"),
        # Add more questions here
    ]
    
    # Add questions to the database
    db.session.add_all(ai_questions)
    db.session.commit()
    print("Database populated with quiz questions!")
