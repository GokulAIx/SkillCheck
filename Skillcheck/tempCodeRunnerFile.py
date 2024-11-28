import logging
import requests
import csv
from flask import Flask, render_template, request
from markupsafe import Markup

# Initialize Flask app
app = Flask(__name__)

# Hugging Face API configuration
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
headers = {"Authorization": "Bearer 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"}

# Set up logging
logging.basicConfig(level=logging.INFO)

# Global cache to avoid re-reading the CSV file repeatedly
cached_questions = None

# Function to load questions from CSV file
def load_questions():
    global cached_questions
    if cached_questions is None:  # Cache questions after the first load
        questions = []
        try:
            with open("quiz_questions.csv", newline="", encoding="utf-8") as file:
                csv_reader = csv.DictReader(file)
                questions.extend(csv_reader)
            cached_questions = questions
        except FileNotFoundError:
            logging.error("Error: quiz_questions.csv not found.")
        except Exception as e:
            logging.error(f"Error loading questions: {e}")
    return cached_questions

# Function to get suggestions from AI for wrong answers
# Function to get explanations from AI for wrong answers
def get_explanations_from_ai(wrong_answers):
    if not wrong_answers:
        return ["No explanation needed. Great job!"]

    explanations = []
    
    for question, user_answer, correct_answer in wrong_answers:
        # Adjusted prompt to request an explanation instead of suggestions
        prompt = f"Explain this quiz question and the reasoning behind the correct answer. Question: {question}, Correct Answer: {correct_answer}, User's Answer: {user_answer}. Provide a detailed explanation."
        
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": prompt, "parameters": {"max_new_tokens": 150, "temperature": 0.7, "top_p": 0.9}},
            )

            if response.status_code == 200:
                response_data = response.json()
                generated_text = response_data[0].get("generated_text", "").strip()

                # Clean and extract the explanation
                clean_explanation = generated_text.replace(prompt, "").strip()

                if clean_explanation:
                    explanations.append(f"**Question**: {question}\n**Correct Answer**: {correct_answer}.\n**Your Answer**: {user_answer}\n**Explanation**: {clean_explanation[:300]}")
                else:
                    explanations.append(f"**Question**: {question}\n**Correct Answer**: {correct_answer}.\n**Your Answer**: {user_answer}\n**Explanation**: Review the reasoning behind the answer for better understanding.")
            else:
                explanations.append(f"**Question**: {question}\n**Correct Answer**: {correct_answer}.\n**Your Answer**: {user_answer}\n**Explanation**: Unable to provide an explanation due to API error.")

        except requests.exceptions.RequestException as e:
            logging.error(f"Error making API request: {e}")
            explanations.append(f"**Question**: {question}\n**Correct Answer**: {correct_answer}.\n**Your Answer**: {user_answer}\n**Explanation**: Additional review is recommended to understand this concept.")

    return list(dict.fromkeys(explanations))[:5]  # Remove duplicates

# Function to get filtered questions based on domain and topic
def get_questions(domain, topic):
    all_questions = load_questions()
    filtered_questions = [q for q in all_questions if q.get("domain", "").strip() == domain.strip() and q.get("topic", "").strip() == topic.strip()]
    return filtered_questions

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Route to display the quiz
@app.route("/quiz", methods=["GET"])
def quiz():
    domain = request.args.get("domain", "")
    topic = request.args.get("topic", "")
    questions = get_questions(domain, topic)
    return render_template("quiz.html", questions=questions, domain=domain, topic=topic)

# Route to handle quiz submission
# Route to handle quiz submission
@app.route("/submit", methods=["POST"])
def submit_quiz():
    domain = request.form.get("domain", "")
    topic = request.form.get("topic", "")
    current_questions = get_questions(domain, topic)
    marks = 0
    wrong_answers = []

    for i, question in enumerate(current_questions, start=1):
        user_answer = request.form.get(f"answer_{i}", "").split(". ", 1)[-1]
        correct_answer = question.get("canswer", "")
        if user_answer == correct_answer:
            marks += 1
        else:
            wrong_answers.append((question["question"], user_answer, correct_answer))

    # Get AI-generated explanations for incorrect answers
    explanations = get_explanations_from_ai(wrong_answers)

    # Markup explanations to allow HTML rendering (like bold formatting)
    marked_explanations = [Markup(explanation) for explanation in explanations]

    return render_template(
        "results.html",
        marks=marks,
        total_questions=len(current_questions),
        explanations=marked_explanations,
    )


if __name__ == "__main__":
    app.run(debug=True)
