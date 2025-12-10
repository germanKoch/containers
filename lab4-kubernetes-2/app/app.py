from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)


def get_db_connection():
    """Create a new database connection using environment variables."""
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    return conn


@app.route("/")
def index():
    return "Hello from Docker lab with Postgres! Visit /items to see data."


@app.route("/items")
def get_items():
    """Return all items from the database as JSON."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM items ORDER BY id;")
            rows = cur.fetchall()
        items = [{"id": row[0], "name": row[1]} for row in rows]
        return jsonify(items)
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
