"""
This is the database module. It contains DB class.
"""

import os
import sqlite3


class CorpusDB():
    """the db of corpora"""

    def __init__(self, path):
        self.path = path
        if not os.path.exists(self.path):
            self.create() # create the database if there's none yet

    def create(self):
        """
        Creates the database.
        """
        db = sqlite3.connect(self.path)
        cur = db.cursor()
        cur.execute('CREATE TABLE sentences (SentNum, sentence, CorpId)')
        cur.execute("""
            CREATE TABLE meta
            (CorpId PRIMARY KEY, corpName, TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)
            """)
        db.commit()

    def write_corpus(self, treebank_id, corpus, corpus_name):
        """
        Writes the corpus data to the database
        """
        db = sqlite3.connect(self.path)
        cur = db.cursor()
        corpus = [(i, sent, treebank_id)
                  for (i, sent) in enumerate(corpus.split('\n\n'))]
        cur.executemany('INSERT INTO sentences VALUES (?, ?, ?)', corpus)
        db.commit()
        cur.execute('INSERT INTO meta (CorpId, corpName) VALUES (?, ?)', (treebank_id, corpus_name))
        db.commit()
        db.close()

    def get_sentence(self, sent_num, treebank_id):
        """
        Takes an integer with sentence number and returns a sentence with this number.
        """
        db = sqlite3.connect(self.path)
        cur = db.cursor()
        cur.execute("""
            SELECT sentence
            FROM sentences
            WHERE SentNum = ? AND CorpId = ?""",
            (int(sent_num) - 1, treebank_id)
            )
        sentence = cur.fetchone()[0]
        db.commit()
        cur.execute("""
            SELECT COUNT(sentence)
            FROM sentences
            WHERE CorpId = (?)""", 
            (treebank_id, ))
        max_sent = cur.fetchone()[0]
        db.commit()
        db.close()
        return sentence, max_sent

    def update_db(self, sentence, treebank_id, sent_num):
        db = sqlite3.connect(self.path)
        cur = db.cursor()
        sent_num = int(sent_num) - 1
        cur.execute("""
            UPDATE sentences
            SET sentence = (?)
            WHERE SentNum = (?) AND CorpId = (?)""",
            (sentence, sent_num, treebank_id))
        db.commit()
        db.close()

    def get_file(self, treebank_id):
        db = sqlite3.connect(self.path)
        cur = db.cursor()
        cur.execute("""
            SELECT sentence
            FROM corpus
            WHERE CorpId = (?)
            ORDER BY SentNum""",
            (treebank_id,)
            )
        corpus = cur.fetchall()
        corpus = '\n\n'.join([tu[0] for tu in corpus])
        db.commit()
        cur.execute('SELECT corp_name FROM meta')
        corpus_name = cur.fetchone()[0]
        db.close()
        return corpus, corpus_name
