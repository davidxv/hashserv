import sqlite3
from contextlib import closing
from flask import Flask, jsonify

# Application imports
from hashserv.DataHash import DataHash
from hashserv.DataBlock import DataBlock


# Initialize the Flask application
app = Flask(__name__)
app.config['DATABASE'] = '/db/hashserv.db'


# Database code
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


# Routes
@app.route('/')
def index():
    return "hello world."


@app.route('/api/submit/<sha256_hash>')
def submit(sha256_hash):
    """Submit a hash to the queue."""
    conn = connect_db()
    datahash = DataHash(sha256_hash, conn)
    if not datahash.is_sha256():
        return "400: Invalid SHA256 Hash."
    else:
        return str(datahash.to_db())


@app.route('/api/block/<block_num>')
def show_block(block_num):
    """Shows the metadata for a particular block."""
    conn = connect_db()

    try:
        block = DataBlock(block_num, conn)
        block.find_leaves()
        return jsonify(block.to_json())
    except LookupError:
        return "Empty Block."

@app.route('/api/block/latest_block')
def latest_block():
    conn = connect_db()
    return str(DataHash(None, conn).latest_block())

if __name__ == '__main__':
    # Run the Flask app
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )