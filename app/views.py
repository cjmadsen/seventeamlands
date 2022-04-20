from app import app
from flask import render_template, redirect, request, jsonify, url_for
import sys
import json
from app.utils import get_tokens
from app.scrape_results import scrape_results, df_ops
from app.metagame_results import get_metagame, get_format_history
from app.card_results import card_stats
import threading
import traceback

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/results', methods = ['GET'])
def results():
    tokens = get_tokens()
    thread = threading.Thread(target=scrape_results, kwargs={
                'tokens': tokens})
    thread.setDaemon(True)
    thread.start()
    return render_template('index.html', response="Script started")


@app.route('/metagame_card_stats', methods=['GET'])
def metagame_card_stats():
    # Run the metagame breakdown script
    args = request.args
    deck_set = args.get('set')
    release_date = args.get('release_date')
    m_msg = ""
    tp_msg = ""
    cs_msg = ""
    if deck_set is not None:
        try:
            m_results = next(get_metagame(deck_set))
            m_code = 200
            if m_results.shape[0] > 0:
                m_msg = "Data returned based on query"
            else:
                m_msg = "No data returned based on query"
        except Exception as e:
            m_code = 400
            m_msg = str(e)
            traceback.print_exc()
        try:
            tp_results = next(get_format_history(deck_set, release_date))
            tp_code = 200
            if tp_results.shape[0] > 0:
                tp_msg = "Data returned based on query"
                if release_date == "":
                    tp_msg += ". Release date not supplied as query, no start date used to get results for get_format_history"
            else:
                tp_msg = "No data returned based on query"
        except Exception as e:
            tp_msg = str(e)
            tp_code = 400
            traceback.print_exc()
        try:
            cs_results = next(card_stats(deck_set))
            cs_code = 200
            if cs_results.shape[0] > 0:
                cs_msg = "Data returned based on query"
            else:
                cs_msg = "No data returned based on query"
        except Exception as e:
            cs_code = 400
            cs_msg = str(e)
            traceback.print_exc()
    else:
        m_code = tp_code = cs_code = 400
        m_msg =  tp_msg = cs_msg = "Missing query parameter for set"

    response = {"metagame": {"status_code": m_code, "msg": m_msg},
    "team perf": {"status_code": tp_code, "msg": tp_msg}, "card_stats": {"status_code": cs_code, "msg": cs_msg}}

    return jsonify(response)

