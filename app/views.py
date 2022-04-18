from app import app
from flask import render_template, redirect, request, jsonify, url_for
import sys
import json
from app.utils import get_tokens
from app.scrape_results import scrape_results, df_ops
import threading
import concurrent.futures

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/results', methods = ['GET'])
def results():
    tokens = get_tokens()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(scrape_results, tokens)
        return_value = future.result()
        print(return_value)
        render_template('index.html', response=return_value)
    thread = threading.Thread(target=scrape_results, kwargs={
                'tokens': tokens})
    thread.setDaemon(True)
    thread.start()

    return render_template('index.html', response="Script started")