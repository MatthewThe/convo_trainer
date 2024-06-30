import os

from flask import Flask, render_template, request, Response
from flask_cors import CORS

import pandas as pd

from vocabulary_progress import WordCounter

app = Flask(__name__)
CORS(app)

word_counters: dict[str, WordCounter] = {}


@app.route("/")
def hello_world():
    return render_template("record_and_transcribe_audio.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    language_code = request.form["language_code"]
    uploaded_file = request.files["file"]

    language_folder = f"./uploads/{language_code}"
    if not os.path.isdir(language_folder):
        os.makedirs(language_folder)
    uploaded_file.save(f"{language_folder}/{uploaded_file.filename}")
    return {}, 200


@app.route("/analyze_text", methods=["POST"])
def add_word_counts():
    timestamp = request.form["timestamp"]
    text = request.form["text"]
    language_code = request.form["language_code"]

    if language_code not in word_counters:
        word_counters[language_code] = WordCounter(language_code)
    result_df_new = word_counters[language_code].add_word_counts(text)

    language_folder = f"./vocabulary_progress/{language_code}"
    if not os.path.isdir(language_folder):
        os.makedirs(language_folder)

    with open(f"{language_folder}/{timestamp}.txt", "w") as text_file:
        text_file.write(text)

    result_df = word_counters[language_code].add_results(result_df_new)
    return (
        Response(result_df.to_json(orient="records"), mimetype="application/json"),
        200,
    )


@app.route("/vocabulary_progress/<language_code>", methods=["GET"])
def vocabulary_progress(language_code):
    if language_code not in word_counters:
        word_counters[language_code] = WordCounter(language_code)
    result_df = word_counters[language_code].get_current_progress()
    return (
        Response(result_df.to_json(orient="records"), mimetype="application/json"),
        200,
    )


@app.route("/vocabulary_stats/<language_code>", methods=["GET"])
def vocabulary_stats(language_code):
    if language_code not in word_counters:
        word_counters[language_code] = WordCounter(language_code)
    result_df = word_counters[language_code].get_current_stats()
    return (
        Response(result_df.to_json(orient="records"), mimetype="application/json"),
        200,
    )

if __name__ == "__main__":
    app.run(debug=True)
