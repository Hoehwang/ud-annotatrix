"""
This is the backend for the annotatrix tool. It allows to save a project
on a server and load it when needed.
"""

import sys
from io import BytesIO
from flask import Flask
from flask import jsonify
from flask import request
from flask import redirect
from flask import send_file
from flask import send_from_directory
from flask import url_for
import os
import uuid
from fine_db import CorpusDB
import config

DB_NAME = 'corpora.db'
WELCOME = '''
*******************************************************************************
* NOW POINT YOUR BROWSER AT: http://127.0.0.1:5317/                           *
*******************************************************************************
'''

app = Flask(__name__, static_folder='../standalone', static_url_path='/annotatrix')
DB = CorpusDB(DB_NAME)


@app.route('/save', methods=['GET', 'POST'])
def save_corpus():
    if request.form:
        sent = request.form['content']
        treebank_id = request.form['treebank_id'].strip('#')
        sent_num = request.form['sentNum']
        DB.update_db(sent, treebank_id, sent_num)
        return jsonify()
    return jsonify()


@app.route('/load', methods=['GET', 'POST'])
def load_sentence():
    if request.form:
        treebank_id = request.form['treebank_id'].strip('#')
        sent_num = request.form['sentNum']
        sent, max_sent = DB.get_sentence(sent_num, treebank_id)
        return jsonify({'content': sent, 'max': max_sent})
    return jsonify()


@app.route('/annotatrix/download', methods=['GET', 'POST'])
def download_corpus():
    if request.args:
        treebank_id = request.args['treebank_id'].strip('#')
        db_path = treebank_id + '.db'
        corpus, corpus_name = db.get_file(treebank_id)
        with open('/tmp/' + treebank_id, 'w') as f: 
            f.write(corpus)
        return send_file('/tmp/' + treebank_id, as_attachment=True, attachment_filename=corpus_name)
    return jsonify({'corpus': 'something went wrong'})


@app.route('/annotatrix/upload', methods=['GET', 'POST'])
def upload_new_corpus():
    if request.method == 'POST':
        f = request.files['file']
        corpus_name = f.filename
        corpus = f.read().decode().strip()
        treebank_id = str(uuid.uuid4())
        DB.write_corpus(treebank_id, corpus, corpus_name)
        return redirect(url_for('corpus_page', treebank_id=treebank_id))
    return jsonify({'something': 'went wrong'})


@app.route('/annotatrix/running', methods=['GET', 'POST'])
def running():
    return jsonify({'status': 'running'})


@app.route('/annotatrix/', methods=['GET', 'POST'])
def annotatrix():
    treebank_id = str(uuid.uuid4())
    return redirect(url_for('corpus_page', treebank_id=treebank_id))


@app.route('/', methods=['GET', 'POST'])
def index():
    return send_from_directory('../standalone', 'welcome_page.html')


@app.route('/annotatrix/<treebank_id>')
def corpus_page(treebank_id):
    if '.' in treebank_id:
        return send_from_directory('../standalone', treebank_id)
    return send_from_directory('../standalone', 'annotator.html')


if __name__ == '__main__':
    print(WELCOME)
    app.secret_key = config.SECRET_KEY
    app.run(debug = True, port = 5317)
