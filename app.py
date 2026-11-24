
from flask import Flask, request, jsonify
from flask_cors import CORS
from contextlib import contextmanager
from dotenv import load_dotenv
import joblib
import pandas as pd
import mysql.connector
import os


# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
CORS(app)


# MySQL database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": os.getenv("DB_PASSWORD"),
    "database": "adhd_project",
    "connection_timeout": 10
}


# Check whether database password is available
if not DB_CONFIG["password"]:
    raise ValueError("DB_PASSWORD not found. Please check your .env file.")


# Create a separate database connection for every request
@contextmanager
def get_db_cursor(dictionary=False):

    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=dictionary)

        yield connection, cursor

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


print("MySQL database configuration ready!")


# Load trained ADHD model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "adhd_model.pkl")

model = joblib.load(MODEL_PATH)

print("ADHD model loaded successfully!")


# ASRS columns used during training
asrs_columns = [f"ASRS_{i}" for i in range(1, 19)]


# Home route
@app.route("/")
def home():
    return "ADHD Screening Backend is Running!"


# User Registration
@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data["name"]
    email = data["email"]
    password = data["password"]
    age = data["age"]

    with get_db_cursor() as (connection, cursor):

        query = """
            INSERT INTO users (name, email, password, age)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (name, email, password, age))

        connection.commit()

        user_id = cursor.lastrowid

    return jsonify({
        "message": "User registered successfully!",
        "user_id": user_id
    })


# User Login
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data["email"]
    password = data["password"]

    with get_db_cursor(dictionary=True) as (connection, cursor):

        query = """
            SELECT user_id, name, email, age
            FROM users
            WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))

        user = cursor.fetchone()

    if user:
        return jsonify({
            "message": "Login successful!",
            "user": user
        })

    return jsonify({
        "message": "Invalid email or password"
    }), 401


# Therapist Registration
@app.route("/therapist-register", methods=["POST"])
def therapist_register():

    data = request.get_json()

    name = data["name"]
    email = data["email"]
    password = data["password"]
    specialization = data["specialization"]
    location = data["location"]
    phone = data["phone"]

    with get_db_cursor() as (connection, cursor):

        query = """
            INSERT INTO therapists
            (name, email, password, specialization, location, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (name, email, password, specialization, location, phone)
        )

        connection.commit()

    return jsonify({
        "message": "Therapist registered successfully!"
    })


# Therapist Login
@app.route("/therapist-login", methods=["POST"])
def therapist_login():

    data = request.get_json()

    email = data["email"]
    password = data["password"]

    with get_db_cursor(dictionary=True) as (connection, cursor):

        query = """
            SELECT therapist_id, name, email, specialization, location, phone
            FROM therapists
            WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))

        therapist = cursor.fetchone()

    if therapist:
        return jsonify({
            "message": "Therapist login successful!",
            "therapist": therapist
        })

    return jsonify({
        "message": "Invalid email or password"
    }), 401


# Search Therapist by Location
@app.route("/therapists/<location>", methods=["GET"])
def search_therapists(location):

    with get_db_cursor(dictionary=True) as (connection, cursor):

        query = """
            SELECT therapist_id, name, specialization, location, phone
            FROM therapists
            WHERE location = %s
        """

        cursor.execute(query, (location,))

        therapists = cursor.fetchall()

    return jsonify(therapists)


# Mood Tracker
@app.route("/mood", methods=["POST"])
def add_mood():

    data = request.get_json()

    user_id = data["user_id"]
    mood = data["mood"]

    with get_db_cursor() as (connection, cursor):

        query = """
            INSERT INTO mood_tracker (user_id, mood, date)
            VALUES (%s, %s, CURDATE())
        """

        cursor.execute(query, (user_id, mood))

        connection.commit()

    return jsonify({
        "message": "Mood saved successfully!"
    })


# View Mood History
@app.route("/mood/<int:user_id>", methods=["GET"])
def view_mood_history(user_id):

    with get_db_cursor(dictionary=True) as (connection, cursor):

        query = """
            SELECT mood_id, mood, date
            FROM mood_tracker
            WHERE user_id = %s
            ORDER BY date DESC
        """

        cursor.execute(query, (user_id,))

        moods = cursor.fetchall()

    return jsonify(moods)


# Add Task
@app.route("/tasks", methods=["POST"])
def add_task():

    data = request.get_json()

    user_id = data["user_id"]
    task = data["task"]

    with get_db_cursor() as (connection, cursor):

        query = """
            INSERT INTO tasks (user_id, task, status)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            query,
            (user_id, task, "Pending")
        )

        connection.commit()

    return jsonify({
        "message": "Task added successfully!"
    })


# View Tasks
@app.route("/tasks/<int:user_id>", methods=["GET"])
def view_tasks(user_id):

    with get_db_cursor(dictionary=True) as (connection, cursor):

        query = """
            SELECT task_id, task, status, created_at
            FROM tasks
            WHERE user_id = %s
        """

        cursor.execute(query, (user_id,))

        tasks = cursor.fetchall()

    return jsonify(tasks)


# Complete Task
@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def complete_task(task_id):

    with get_db_cursor() as (connection, cursor):

        query = """
            UPDATE tasks
            SET status = 'Completed'
            WHERE task_id = %s
        """

        cursor.execute(query, (task_id,))

        connection.commit()

    return jsonify({
        "message": "Task completed successfully!"
    })


# Delete Task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    with get_db_cursor() as (connection, cursor):

        query = """
            DELETE FROM tasks
            WHERE task_id = %s
        """

        cursor.execute(query, (task_id,))

        connection.commit()

    return jsonify({
        "message": "Task deleted successfully!"
    })


# ADHD Screening Prediction
@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    user_id = data["user_id"]
    answers = data["answers"]

    if len(answers) != 18:
        return jsonify({
            "message": "Please provide all 18 answers."
        }), 400

    input_data = pd.DataFrame(
        [answers],
        columns=asrs_columns
    )

    prediction = model.predict(input_data)[0]

    if prediction == 1.0:
        result = "Screening result indicates a possibility of ADHD symptoms."
    else:
        result = "Screening result does not indicate a strong possibility of ADHD symptoms."

    # Save screening result in MySQL
    with get_db_cursor() as (connection, cursor):

        query = """
            INSERT INTO screening_results (user_id, prediction, date)
            VALUES (%s, %s, CURDATE())
        """

        cursor.execute(
            query,
            (user_id, str(prediction))
        )

        connection.commit()

    return jsonify({
        "prediction": float(prediction),
        "screening_result": result
    })


# View Screening Result History
@app.route("/screening-results/<int:user_id>", methods=["GET"])
def view_screening_results(user_id):

    with get_db_cursor(dictionary=True) as (connection, cursor):

        query = """
            SELECT result_id, prediction, date
            FROM screening_results
            WHERE user_id = %s
            ORDER BY date DESC
        """

        cursor.execute(query, (user_id,))

        results = cursor.fetchall()

    return jsonify(results)


# Run Flask server
if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False,
        host="127.0.0.1",
        port=5000
    )
