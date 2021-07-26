import json
import unittest

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text as sa_text

from game_store.app import create_app
from game_store.models import Game, setup_db

test_game = Game('test', 'test', 'test')


def expected_404_builder(message):
    return {
        "success": False,
        "error": 404,
        "message": message
    }


def expected_422_builder(message):
    return {
        "success": False,
        "error": 422,
        "message": message
    }


class GameStore(unittest.TestCase):

    @staticmethod
    def add_game(game=None):
        if game is None:
            test_game.insert()
        else:
            game.insert()

    @staticmethod
    def remove_default_game():
        test_game.delete()

    def setUp(self, test_config=None):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "game_store_test"
        self.database_path = "postgresql://test:test@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.drop_all()
            self.db.create_all()

    def tearDown(self):
        # remove any data between tests
        with self.app.app_context():
            try:
                self.db.engine.execute(
                    sa_text('''TRUNCATE TABLE games RESTART IDENTITY CASCADE ''').execution_options(
                        autocommit=True))
                self.db.engine.execute(
                    sa_text('''TRUNCATE TABLE consoles RESTART IDENTITY CASCADE ''').execution_options(
                        autocommit=True))
            except:
                self.db.session.rollback()

            self.db.session.close()
        pass

    def test_get_games__returns_games_from_database(self):
        with self.app.app_context():
            self.add_game(Game('Final Fantasy', "RPG", "NES"))

        res = self.client().get('/games')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        games = data['games']
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0], {'console': 'NES', 'genre': 'RPG', 'id': 1, 'name': 'Final Fantasy'})

    def test_get_games__no_games_in_database__returns_404_error(self):
        res = self.client().get('/games')

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('No games found'), actual_response)

    def test_get_game__returns_game_with_matching_id(self):
        with self.app.app_context():
            self.add_game(Game('wat', 'idk', 'idc'))
            self.add_game(Game('Final Fantasy', "RPG", "NES"))

        res = self.client().get('/games/2')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        game = data['game']
        self.assertEqual(game, {'console': 'NES', 'genre': 'RPG', 'id': 2, 'name': 'Final Fantasy'})

    def test_get_games__game_not_in_database__returns_404_error(self):
        res = self.client().get('/games/100')

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('Game not found'), actual_response)

    def test_add_game__adds_new_game_to_database(self):

        request_body = {
            'name': "WarCraft 3",
            'genre': 'RTS',
            'console': 'PC'
        }

        post_res = self.client().post('/games', json=request_body)

        self.assertEqual(post_res.status_code, 204)

        res = self.client().get('/games')
        data = json.loads(res.data)
        games = data['games']
        self.assertEqual(games[0], {'console': request_body['console'],
                                    'genre': request_body['genre'],
                                    'id': 1,
                                    'name': request_body['name']})

    def test_add_game__add_a_game_that_without_a_name__return_a_422(self):

        request_body = {
            'genre': 'RTS',
            'console': 'PC'
        }

        post_res = self.client().post('/games', json=request_body)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Game must have a name'), actual_response)

    def test_get_game__new_name_is_passed_in__returns_game_with_matching_id(self):
        with self.app.app_context():
            self.add_game(Game('Final Fantasy', "RPG", "NES"))

        res = self.client().put('/games/1', json={'name': 'Final Fantasy 2'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/games/1')

        data = json.loads(res.data)
        game = data['game']
        self.assertEqual(game, {'console': 'NES', 'genre': 'RPG', 'id': 1, 'name': 'Final Fantasy 2'})

    def test_get_game__new_genre_is_passed_in__returns_game_with_matching_id(self):
        with self.app.app_context():
            self.add_game(Game('Final Fantasy', "RPG", "NES"))

        res = self.client().put('/games/1', json={'genre': 'Rhythm'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/games/1')

        data = json.loads(res.data)
        game = data['game']
        self.assertEqual(game, {'console': 'NES', 'genre': 'Rhythm', 'id': 1, 'name': 'Final Fantasy'})

    def test_get_game__new_console_is_passed_in__returns_game_with_matching_id(self):
        with self.app.app_context():
            self.add_game(Game('Final Fantasy', "RPG", "NES"))

        res = self.client().put('/games/1', json={'console': 'SNES'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/games/1')

        data = json.loads(res.data)
        game = data['game']
        self.assertEqual(game, {'console': 'SNES', 'genre': 'RPG', 'id': 1, 'name': 'Final Fantasy'})

    def test_get_game__updating_game_not_in_database__returns_404_error(self):
        res = self.client().put('/games/400', json={'name': 'No game here'})
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not update, game does not exist'), actual_response)

    def test_get_game__no_request_body__returns_422_error(self):
        res = self.client().put('/games/1')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Request missing body'), actual_response)

    def test_get_game__no_update_data_passed_in__returns_422_error(self):
        res = self.client().put('/games/1', json={})
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Must include a value to update'), actual_response)

    def test_delete_game__deletes_game_from_database(self):
        with self.app.app_context():
            self.add_game()
            self.add_game(Game('Final Fantasy', "RPG", "NES"))

        res = self.client().get('/games')
        data = json.loads(res.data)
        self.assertEqual(2, len(data['games']))

        res = self.client().delete('/games/2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/games')
        data = json.loads(res.data)
        self.assertEqual(1, len(data['games']))

        res = self.client().get('/games/2')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Game not found'), actual_response)

    def test_delete_game__game_not_in_database__deletes_game_from_database(self):
        res = self.client().delete('/games/400000')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not delete, game does not exist'), actual_response)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
