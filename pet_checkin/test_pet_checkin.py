import json
import unittest

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text as sa_text

from app import create_app
from models import Pet, setup_db, Owner


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


class PetCheckin(unittest.TestCase):

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
                    sa_text('''TRUNCATE TABLE owners RESTART IDENTITY CASCADE ''').execution_options(
                        autocommit=True))
                self.db.engine.execute(
                    sa_text('''TRUNCATE TABLE pets RESTART IDENTITY CASCADE ''').execution_options(
                        autocommit=True))
            except:
                self.db.session.rollback()

            self.db.session.close()
        pass

    '''
    Owners Tests
    '''

    def test_get_owners__returns_owners_from_database(self):
        with self.app.app_context():
            Owner('Bob', "321-456-0987").insert()

        res = self.client().get('/owners')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        owners = data['owners']
        self.assertEqual(len(owners), 1)
        self.assertEqual(owners[0], {'id': 1, 'name': 'Bob', 'phone': '321-456-0987'})

    def test_get_owners__no_owners_in_database__returns_404_error(self):
        res = self.client().get('/owners')

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('No owners found'), actual_response)

    def test_get_owner__returns_owner_with_matching_id(self):
        with self.app.app_context():
            Owner('Who dat?', "111-222-0000").insert()
            Owner('Jim', "222-222-2222").insert()

        res = self.client().get('/owners/2')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        owner = data['owner']
        self.assertEqual(owner, {'name': 'Jim', 'phone': '222-222-2222', 'id': 2})

    def test_get_owners__owner_not_in_database__returns_404_error(self):
        res = self.client().get('/owners/100')

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('Owner not found'), actual_response)

    def test_add_owner__adds_new_owner_to_database(self):

        request_body = {
            'name': "Dude",
            'phone': '111-222-3333'
        }

        post_res = self.client().post('/owners', json=request_body)

        self.assertEqual(post_res.status_code, 204)

        res = self.client().get('/owners')
        data = json.loads(res.data)
        owners = data['owners']
        self.assertEqual(owners[0], {'name': request_body['name'],
                                     'id': 1,
                                     'phone': request_body['phone']})

    def test_add_owner__add_a_owner_that_without_a_name__return_a_422(self):

        request_body = {
            'phone': '321-654-0987'
        }

        post_res = self.client().post('/owners', json=request_body)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Owner must have a name'), actual_response)

    def test_add_owner__add_a_owner_that_without_a_phone_number__return_a_422(self):

        request_body = {
            'name': 'No phone'
        }

        post_res = self.client().post('/owners', json=request_body)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Owner must have a phone number'), actual_response)

    def test_update_owner__new_name_is_passed_in__updates_owner(self):
        with self.app.app_context():
            Owner('Jim', "222-222-2222").insert()

        res = self.client().put('/owners/1', json={'name': 'I am new owner name'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/owners/1')

        data = json.loads(res.data)
        owner = data['owner']
        self.assertEqual(owner, {'name': 'I am new owner name', 'phone': '222-222-2222', 'id': 1})

    def test_update_owner__new_phone_number_is_passed_in__updates_owner(self):
        with self.app.app_context():
            Owner('Jim', "222-222-2222").insert()

        res = self.client().put('/owners/1', json={'phone': '098-765-4321'})

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/owners/1')

        data = json.loads(res.data)
        owner = data['owner']
        self.assertEqual(owner, {'name': 'Jim', 'phone': '098-765-4321', 'id': 1})

    def test_update_owner__updating_owner_not_in_database__returns_404_error(self):
        res = self.client().put('/owners/400', json={'name': 'No owner here'})
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not update, owner does not exist'), actual_response)

    def test_update_owner__no_request_body__returns_422_error(self):
        res = self.client().put('/owners/1')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Request missing body'), actual_response)

    def test_update_owner__no_update_data_passed_in__returns_422_error(self):
        res = self.client().put('/owners/1', json={})
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Must include a value to update'), actual_response)

    def test_delete_owner__deletes_owner_from_database(self):
        with self.app.app_context():
            Owner('who', '111-111-1111').insert()
            Owner('Doggo Owner', '444-444-4444').insert()

        res = self.client().get('/owners')
        data = json.loads(res.data)
        self.assertEqual(2, len(data['owners']))

        res = self.client().delete('/owners/2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/owners')
        data = json.loads(res.data)
        self.assertEqual(1, len(data['owners']))

        res = self.client().get('/owners/2')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Owner not found'), actual_response)

    def test_delete_owner__owner_not_in_database__returns_404_error(self):
        res = self.client().delete('/owners/400000')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not delete, owner does not exist'), actual_response)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
