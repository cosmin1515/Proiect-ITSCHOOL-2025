import unittest
from app import app  # Assumes the app is in a file called `app.py`

class FlaskAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Sets up the Flask app for testing."""
        cls.client = app.test_client()
        app.config['TESTING'] = True

    def test_home(self):
        """Test the home route."""
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'Welcome to the Rock-Paper-Scissors API!')

    def test_create_user(self):
        """Test creating a user."""
        data = {'username': 'test_user'}
        response = self.client.post('/create_user', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('user_id', response.json)

    def test_play_game(self):
        """Test the game play."""
        user_data = {'username': 'player1'}
        response_create = self.client.post('/create_user', json=user_data)
        user_id = response_create.json['user_id']

        game_data = {'user_id': user_id, 'move': 'piatra'}
        response_game = self.client.post('/start_game', json=game_data)
        self.assertEqual(response_game.status_code, 200)
        self.assertIn('player_move', response_game.json)
        self.assertIn('ai_move', response_game.json)
        self.assertIn('result', response_game.json)

    def test_get_scores(self):
        """Test getting scores for a user."""
        user_data = {'username': 'player2'}
        response_create = self.client.post('/create_user', json=user_data)
        user_id = response_create.json['user_id']

        game_data = {'user_id': user_id, 'move': 'hartie'}
        self.client.post('/start_game', json=game_data)

        response = self.client.get(f'/get_scores/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('score_player', response.json)
        self.assertIn('score_ai', response.json)

    def test_invalid_move(self):
        """Test invalid move in a game."""
        user_data = {'username': 'player3'}
        response_create = self.client.post('/create_user', json=user_data)
        user_id = response_create.json['user_id']

        game_data = {'user_id': user_id, 'move': 'nevalid'}
        response = self.client.post('/start_game', json=game_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

if __name__ == '__main__':
    unittest.main()
