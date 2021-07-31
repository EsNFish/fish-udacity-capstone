import json
import unittest

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text as sa_text

from app import create_app
from models import Pet, setup_db


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


class PetEndpoints(unittest.TestCase):

    def setUp(self, test_config=None):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "pet_checkin_test"
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
                    sa_text('''TRUNCATE TABLE pets RESTART IDENTITY CASCADE ''').execution_options(
                        autocommit=True))
                self.db.engine.execute(
                    sa_text('''TRUNCATE TABLE pets RESTART IDENTITY CASCADE ''').execution_options(
                        autocommit=True))
            except:
                self.db.session.rollback()

            self.db.session.close()
        pass

    '''
    Pet Tests
    '''

    def test_get_pets__returns_pets_from_database(self):
        with self.app.app_context():
            Pet('Fifi', "dog", "pug").insert()

        res = self.client().get('/pets')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        pets = data['pets']
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0], {'id': 1, 'name': 'Fifi', 'species': 'dog', 'breed': 'pug'})

    def test_get_pets__no_pets_in_database__returns_404_error(self):
        res = self.client().get('/pets')

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('No pets found'), actual_response)

    def test_get_pet__returns_pet_with_matching_id(self):
        with self.app.app_context():
            Pet('Fifi', "dog", "pug").insert()
            Pet('Libby', "dog", "black lab").insert()

        res = self.client().get('/pets/2')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        pet = data['pet']
        self.assertEqual(pet, {'id': 2, 'name': 'Libby', 'species': 'dog', 'breed': 'black lab'})

    def test_get_pets__pet_not_in_database__returns_404_error(self):
        res = self.client().get('/pets/100')

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('Pet not found'), actual_response)

    def test_add_pet__adds_new_pet_to_database(self):

        request_body = {
            'name': "Scrabble",
            'species': 'dog',
            'breed': 'Boxer'
        }

        post_res = self.client().post('/pets', json=request_body)

        self.assertEqual(post_res.status_code, 204)

        res = self.client().get('/pets')
        data = json.loads(res.data)
        pets = data['pets']
        self.assertEqual(pets[0], {'name': request_body['name'],
                                   'id': 1,
                                   'species': request_body['species'],
                                   'breed': request_body['breed']})

    def test_add_pet__add_a_pet_that_without_a_name__return_a_422(self):

        request_body = {
            'breed': '321-654-0987'
        }

        post_res = self.client().post('/pets', json=request_body)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Pet must have a name'), actual_response)

    def test_add_pet__add_a_pet_that_without_a_species__return_a_422(self):

        request_body = {
            'name': 'No species'
        }

        post_res = self.client().post('/pets', json=request_body)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Pet must have a species'), actual_response)

    def test_update_pet__new_name_is_passed_in__updates_pet(self):
        with self.app.app_context():
            Pet('Fifi', "dog", "pug").insert()

        res = self.client().put('/pets/1', json={'name': 'I am new pet name'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/pets/1')

        data = json.loads(res.data)
        pet = data['pet']
        self.assertEqual(pet, {'name': 'I am new pet name', 'species': 'dog', 'breed' : 'pug', 'id': 1})

    def test_update_pet__new_species_is_passed_in__updates_pet(self):
        with self.app.app_context():
            Pet('Fifi', "dog", "pug").insert()

        res = self.client().put('/pets/1', json={'species': 'cat?'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/pets/1')

        data = json.loads(res.data)
        pet = data['pet']
        self.assertEqual(pet, {'name': 'Fifi', 'species': 'cat?', 'breed': 'pug', 'id': 1})

    def test_update_pet__new_breed_is_passed_in__updates_pet(self):
        with self.app.app_context():
            Pet('Fifi', "dog", "pug").insert()

        res = self.client().put('/pets/1', json={'breed': 'French Bulldog'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/pets/1')

        data = json.loads(res.data)
        pet = data['pet']
        self.assertEqual(pet, {'name': 'Fifi', 'species': 'dog', 'breed': 'French Bulldog', 'id': 1})

    def test_update_pet__updating_pet_not_in_database__returns_404_error(self):
        res = self.client().put('/pets/400', json={'name': 'No pet here'})
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not update, pet does not exist'), actual_response)

    def test_update_pet__no_request_body__returns_422_error(self):
        res = self.client().put('/pets/1')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Request missing body'), actual_response)

    def test_update_pet__no_update_data_passed_in__returns_422_error(self):
        res = self.client().put('/pets/1', json={})
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Must include a value to update'), actual_response)

    def test_delete_pet__deletes_pet_from_database(self):
        with self.app.app_context():
            Pet('Fifi', "dog", "pug").insert()
            Pet('Libby', "dog", "black lab").insert()

        res = self.client().get('/pets')
        data = json.loads(res.data)
        self.assertEqual(2, len(data['pets']))

        res = self.client().delete('/pets/2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/pets')
        data = json.loads(res.data)
        self.assertEqual(1, len(data['pets']))

        res = self.client().get('/pets/2')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Pet not found'), actual_response)

    def test_delete_pet__pet_not_in_database__returns_404_error(self):
        res = self.client().delete('/pets/400000')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not delete, pet does not exist'), actual_response)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
