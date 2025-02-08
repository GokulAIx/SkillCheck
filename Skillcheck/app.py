import logging
import requests
import csv
import random
from flask import Flask, render_template, request
# Initialize Flask app
app = Flask(__name__)

# Groq API configuration
API_URL = "https://api.groq.com/openai/v1/chat/completions"
headers = {"Authorization": "Bearer ", "Content-Type": "application/json"}

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

# Function to get explanations from Groq LLaMA model for wrong answers
def get_explanations_from_ai(wrong_answers):
    if not wrong_answers:
        return ["No explanation needed. Great job!"]

    explanations = []

    for question, user_answer, correct_answer in wrong_answers:
        # Adjusted prompt for LLaMA model to request an explanation
        prompt = f"Explain this quiz question and the reasoning behind the correct answer. in 5 lines. Question: {question}, Correct Answer: {correct_answer}, User's Answer: {user_answer}. Provide a detailed explanation."

        try:
            # API request to Groq model
            response = requests.post(
                API_URL,
                headers=headers,
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }]
                },
            )

            # Log the full response for debugging
            if response.status_code != 200:
                logging.error(f"API request failed with status code {response.status_code}: {response.text}")

            if response.status_code == 200:
                response_data = response.json()
                generated_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

                # Clean and extract the explanation
                clean_explanation = generated_text.strip()

                if clean_explanation:
                    explanation_lines = clean_explanation.split("\n")
                    formatted_explanation = "\n".join([line.strip() for line in explanation_lines if line.strip()])
                    explanations.append(f"**Question**: {question}\n**Correct Answer**: {correct_answer}.\n**Your Answer**: {user_answer}\n**Explanation**: {formatted_explanation}")
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
    selected=random.sample(filtered_questions,5)
    return selected

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
