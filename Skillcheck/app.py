from flask import Flask, render_template, request
import csv

app = Flask(__name__)

# Load questions from the CSV file
def load_questions():
    questions = []
    try:
        with open('quiz_questions.csv', newline='', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            # Print column names to verify
            print("CSV Column Names:", csv_reader.fieldnames)
            
            for row in csv_reader:
                # Print each row to see exactly what's being read
                print("Row:", row)
                questions.append(row)
    except FileNotFoundError:
        print("Error: quiz_questions.csv not found.")
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return questions

# Get questions filtered by domain and topic
def get_questions(domain, topic):
    all_questions = load_questions()
    
    # Print debugging information
    print("Filtering Questions:")
    print(f"Looking for Domain: '{domain}', Topic: '{topic}'")
    
    filtered_questions = [
        q for q in all_questions 
        if q.get('domain', '').strip() == domain.strip() and 
           q.get('topic', '').strip() == topic.strip()
    ]
    
    # Print filtered questions
    print("Filtered Questions:", filtered_questions)
    
    return filtered_questions

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Route to display the quiz
@app.route('/quiz', methods=['GET'])
def quiz():
    domain = request.args.get('domain', '')
    topic = request.args.get('topic', '')
    questions = get_questions(domain, topic)
    
    # Debugging: Check the domain and topic values
    print(f"Domain: {domain}, Topic: {topic}")
    print(f"Questions: {questions}")
    
    return render_template('quiz.html', questions=questions, domain=domain, topic=topic)

# Route to handle quiz submission
# Route to handle quiz submission
@app.route('/submit', methods=['POST'])
def submit_quiz():
    # Get domain and topic from the form submission
    domain = request.form.get('domain', '')
    topic = request.form.get('topic', '')
    
    # Get only the questions for this specific quiz
    current_questions = get_questions(domain, topic)
    
    marks = 0
    suggestions = []

    # Print detailed debugging information
    print("Form Data:", dict(request.form))
    print("Current Quiz Questions:", current_questions)

    for i, question in enumerate(current_questions, start=1):
        # Get the user's answer for this specific question
        user_answer = request.form.get(f'answer_{i}', '').split('. ', 1)[-1]
        correct_answer = question.get('canswer', '')

        print(f"Question {i}:")
        print(f"  User Answer: '{user_answer}'")
        print(f"  Correct Answer: '{correct_answer}'")

        if user_answer == correct_answer:
            marks += 1
            print("Correct!")
        else:
            print("Incorrect.")

    print(f"Total Marks: {marks}")
    
    # Suggestions based on marks
    if marks >= len(current_questions) * 0.8:  # 80% or more correct
        suggestions.append("Excellent! Keep up the great work!")
    elif marks >= len(current_questions) * 0.5:  # 50% or more correct
        suggestions.append("Good job, but there's room for improvement.")
    else:
        suggestions.append("Don't worry, try reviewing the material and attempt again!")

    return render_template('results.html', marks=marks, total_questions=len(current_questions), suggestions=suggestions)

if __name__ == '__main__':
    app.run(debug=True)
