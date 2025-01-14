# Rock-Paper-Scissors Flask API

## Testing with Postman

### 1. Home Page
**GET** `/home`
- **URL**: `http://127.0.0.1:5000/home`
- **Method**: `GET`
- **Response**: A welcome message.

### 2. Create User
**POST** `/create_user`
- **URL**: http://127.0.0.1:5000/create_user
- **Method**: `POST`
- **Headers**:
  - `Content-Type: application/json`
- **Body** (raw JSON):
  ```json
  {
    "username": "test_user"
  }
Response:
json

{
  "message": "User created successfully",
  "user_id": 1
}
3. Start Game
POST /start_game

URL: http://127.0.0.1:5000/start_game
Method: POST
Headers:
Content-Type: application/json
Body (raw JSON):
json

{
  "user_id": 1,
  "move": "piatra"
}
Response:
json

{
  "player_move": "piatra",
  "ai_move": "hartie",
  "result": "loss"
}
4. Get Scores
GET /get_scores/{user_id}

URL: http://127.0.0.1:5000/get_scores/1
Method: GET
Response:
json

{
  "score_player": 0,
  "score_ai": 1
}
