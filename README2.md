from flask import Flask, request, jsonify  # Importă clasele necesare din Flask
import random  # Importă modulul random pentru a alege aleatoriu
import sqlite3  # Importă modulul sqlite3 pentru a interacționa cu baza de date

app = Flask(__name__)  # Creează instanța aplicației Flask

# Database setup
DB_NAME = "game.db"  # Definește numele bazei de date

# Inițializarea bazei de date
def init_db():  # Funcție pentru a crea tabelele în baza de date
    with sqlite3.connect(DB_NAME) as conn:  # Creează o conexiune la baza de date
        cursor = conn.cursor()  # Creează un cursor pentru a executa comenzi SQL
        cursor.execute("""  # Creează tabelul `users` dacă nu există deja
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  # Cheie primară auto-incrementată
                username TEXT UNIQUE NOT NULL  # Nume utilizator unic
            )
        """)
        cursor.execute("""  # Creează tabelul `game` dacă nu există deja
            CREATE TABLE IF NOT EXISTS game (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  # Cheie primară auto-incrementată
                score_player INTEGER NOT NULL DEFAULT 0,  # Scorul jucătorului
                score_ai INTEGER NOT NULL DEFAULT 0,  # Scorul AI-ului
                user_id INTEGER NOT NULL,  # ID-ul utilizatorului
                FOREIGN KEY (user_id) REFERENCES users(id)  # Relația între utilizator și joc
            )
        """)
        conn.commit()  # Confirmă modificările în baza de date

# Initializează baza de date la pornirea aplicației
init_db()

# Game logic
OPTIONS = ["piatra", "hartie", "foarfeca"]  # Definirea opțiunilor pentru jocul "piatră, hârtie, foarfecă"

def determine_winner(player_move, ai_move):  # Funcție care determină câștigătorul jocului
    if player_move == ai_move:  # Dacă jucătorul și AI-ul au făcut aceeași mișcare
        return 0  # Egalitate
    elif (player_move == "piatra" and ai_move == "foarfeca") or \
            (player_move == "hartie" and ai_move == "piatra") or \
            (player_move == "foarfeca" and ai_move == "hartie"):  # Condițiile în care jucătorul câștigă
        return 1  # Jucătorul câștigă
    else:  # Dacă AI-ul câștigă
        return -1  # AI-ul câștigă

# Routes (endpoints)
@app.route("/home", methods=["GET"])  # Ruta pentru pagina de start
def home():
    return jsonify({"message": "Welcome to the Rock-Paper-Scissors API!"}), 200  # Mesaj de bun venit

@app.route("/create_user", methods=["POST"])  # Ruta pentru crearea unui utilizator
def user_create():
    username = request.json.get("username")  # Preia numele de utilizator din corpul cererii JSON
    if not username:  # Verifică dacă numele de utilizator este furnizat
        return jsonify({"error": "Username is required"}), 400  # Răspunde cu eroare dacă nu există

    try:
        with sqlite3.connect(DB_NAME) as conn:  # Conectează-te la baza de date
            cursor = conn.cursor()  # Creează un cursor pentru a executa comenzi SQL
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))  # Inserează utilizatorul în tabelul `users`
            conn.commit()  # Confirmă modificările
            user_id = cursor.lastrowid  # Obține ID-ul utilizatorului nou creat
        return jsonify({"message": "User created successfully", "user_id": user_id}), 201  # Returnează un mesaj de succes
    except sqlite3.IntegrityError:  # Dacă numele de utilizator există deja
        return jsonify({"error": "Username already exists"}), 400  # Returnează eroare
    except Exception as e:  # În caz de altă eroare
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 500  # Returnează eroare generală

@app.route("/start_game", methods=["POST"])  # Ruta pentru începerea unui joc
def play():
    user_id = request.json.get("user_id")  # Preia ID-ul utilizatorului din cererea JSON
    player_move = request.json.get("move")  # Preia mișcarea jucătorului din cererea JSON

    if not user_id or player_move not in OPTIONS:  # Verifică dacă inputul este valid
        return jsonify({"error": "Invalid input. Ensure 'user_id' is provided and move is valid."}), 400  # Returnează eroare dacă inputul nu este valid

    ai_move = random.choice(OPTIONS)  # Alege aleatoriu o mișcare pentru AI
    result = determine_winner(player_move, ai_move)  # Determină câștigătorul

    try:
        with sqlite3.connect(DB_NAME) as conn:  # Conectează-te la baza de date
            cursor = conn.cursor()  # Creează un cursor pentru a executa comenzi SQL

            cursor.execute("SELECT * FROM game WHERE user_id = ?", (user_id,))  # Verifică dacă există deja un joc pentru utilizator
            game = cursor.fetchone()  # Preia datele jocului

            if not game:  # Dacă nu există un joc, creează unul
                cursor.execute("INSERT INTO game (user_id) VALUES (?)", (user_id,))
                conn.commit()  # Confirmă modificările

            if result == 1:  # Dacă jucătorul câștigă
                cursor.execute("UPDATE game SET score_player = score_player + 1 WHERE user_id = ?", (user_id,))
            elif result == -1:  # Dacă AI-ul câștigă
                cursor.execute("UPDATE game SET score_ai = score_ai + 1 WHERE user_id = ?", (user_id,))

            conn.commit()  # Confirmă modificările

        return jsonify({  # Returnează mișcările și rezultatul jocului
            "player_move": player_move,
            "ai_move": ai_move,
            "result": "win" if result == 1 else "loss" if result == -1 else "tie"
        }), 200
    except Exception as e:  # În caz de eroare
        return jsonify({"error": f"Failed to process game: {str(e)}"}), 500  # Returnează eroare generală

@app.route("/get_scores/<int:user_id>", methods=["GET"])  # Ruta pentru obținerea scorurilor unui utilizator
def get_scores(user_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:  # Conectează-te la baza de date
            cursor = conn.cursor()  # Creează un cursor pentru a executa comenzi SQL
            cursor.execute("SELECT score_player, score_ai FROM game WHERE user_id = ?", (user_id,))  # Preia scorurile pentru utilizatorul respectiv
            scores = cursor.fetchone()  # Preia rezultatul interogării

        if not scores:  # Dacă nu există scoruri pentru utilizatorul respectiv
            return jsonify({"error": "No scores found for this user"}), 404  # Returnează eroare

        return jsonify({  # Returnează scorurile
            "score_player": scores[0],
            "score_ai": scores[1]
        }), 200
    except Exception as e:  # În caz de eroare
        return jsonify({"error": f"Failed to fetch scores: {str(e)}"}), 500  # Returnează eroare generală

if __name__ == "__main__":  # Dacă fișierul este rulant direct
    app.run(debug=True)  # Pornește aplicația în modul debug
