from flask import Flask, request, jsonify
import random
import sqlite3

app = Flask(__name__)

# Database setup
DB_NAME = "game.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score_player INTEGER NOT NULL DEFAULT 0,
                score_ai INTEGER NOT NULL DEFAULT 0,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()


# Initialize the database
init_db()

# Game logic
OPTIONS = ["piatra", "hartie", "foarfeca"]


def determine_winner(player_move, ai_move):
    if player_move == ai_move:
        return 0
    elif (player_move == "piatra" and ai_move == "foarfeca") or \
            (player_move == "hartie" and ai_move == "piatra") or \
            (player_move == "foarfeca" and ai_move == "hartie"):
        return 1
    else:
        return -1


# Routes (endpoints)
@app.route("/home", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Rock-Paper-Scissors API!"}), 200


@app.route("/create_user", methods=["POST"])
def user_create():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            user_id = cursor.lastrowid
        return jsonify({"message": "User created successfully", "user_id": user_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 500


@app.route("/start_game", methods=["POST"])
def play():
    user_id = request.json.get("user_id")
    player_move = request.json.get("move")

    if not user_id or player_move not in OPTIONS:
        return jsonify({"error": "Invalid input. Ensure 'user_id' is provided and move is valid."}), 400

    ai_move = random.choice(OPTIONS)
    result = determine_winner(player_move, ai_move)

    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM game WHERE user_id = ?", (user_id,))
            game = cursor.fetchone()

            if not game:
                cursor.execute("INSERT INTO game (user_id) VALUES (?)", (user_id,))
                conn.commit()

            if result == 1:
                cursor.execute("UPDATE game SET score_player = score_player + 1 WHERE user_id = ?", (user_id,))
            elif result == -1:
                cursor.execute("UPDATE game SET score_ai = score_ai + 1 WHERE user_id = ?", (user_id,))

            conn.commit()

        return jsonify({
            "player_move": player_move,
            "ai_move": ai_move,
            "result": "win" if result == 1 else "loss" if result == -1 else "tie"
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to process game: {str(e)}"}), 500


@app.route("/get_scores/<int:user_id>", methods=["GET"])
def get_scores(user_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT score_player, score_ai FROM game WHERE user_id = ?", (user_id,))
            scores = cursor.fetchone()

        if not scores:
            return jsonify({"error": "No scores found for this user"}), 404

        return jsonify({
            "score_player": scores[0],
            "score_ai": scores[1]
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch scores: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
