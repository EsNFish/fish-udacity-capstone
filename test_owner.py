import json
import unittest

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text as sa_text

from app import create_app
from models import setup_db, Owner

vet_tech_header = {
    'Authorization': 'Bearer ' + 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImlvM19qSTVheFBZSWRwUVBBYzFWYyJ9.eyJpc3MiOiJodHRwczovL3BldC1jaGVja2luLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MTA4ODg4NTM1ODJiYzAwNjk0N2IyZWEiLCJhdWQiOiJwZXQtY2hlY2tpbiIsImlhdCI6MTYyODExNTQxNiwiZXhwIjoxNjI4MTIyNjE2LCJhenAiOiJoNFI4Z2w4WXJRdzgwcHlGMWt4Y1NqN25mVGd1YWFpZiIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZ2V0LWFwcG9pbnRtZW50cyIsImdldC1vd25lcnMiLCJnZXQtcGV0cyIsInBvc3QtYXBwb2ludG1lbnRzIiwicG9zdC1vd25lcnMiLCJwb3N0LXBldHMiLCJwdXQtYXBwb2ludG1lbnRzIiwicHV0LW93bmVycyIsInB1dC1wZXRzIl19.hOgPoVLjhCmF29aaKf6EPBjuNYnCXekfc4ZCcgIGLXuMqtETZYRA7BbDLSEoJozhtRzdrBlGANj81Xa4ql7cuSaiAFohzj3xpBhdUuVMkMc9wy8EysnL5aUtr9PIGPvDHjoHH-gKZ-UVo6zesG4N9nYacSTT-MJ96yzChLK6JX5WwSZAeufcRTpEOiCHvRLSsBO5xJQ3Z0iWz8Mdh9Y7QPC0QrZ51Lvv1tev0n9hxhr8tk-iPzTxnq4BKgcz2bTuQbA_KJNu1MbDtf75ILOonP6w2Fu3iIG-R5iwvHlEzVS2vgOX0CR6h2o905IRW4sxa-LoOSqTz5SKRURduoZaWg'
}

vet_manager_header = {
    'Authorization': 'Bearer ' + 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImlvM19qSTVheFBZSWRwUVBBYzFWYyJ9.eyJpc3MiOiJodHRwczovL3BldC1jaGVja2luLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MTBhZjQyYjI0NTRmMjAwNmEyNTY1OTMiLCJhdWQiOiJwZXQtY2hlY2tpbiIsImlhdCI6MTYyODExNTY4NiwiZXhwIjoxNjI4MTIyODg2LCJhenAiOiJoNFI4Z2w4WXJRdzgwcHlGMWt4Y1NqN25mVGd1YWFpZiIsInNjb3BlIjoiIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlLWFwcG9pbnRtZW50cyIsImRlbGV0ZS1vd25lcnMiLCJkZWxldGUtcGV0cyIsImdldC1hcHBvaW50bWVudHMiLCJnZXQtb3duZXJzIiwiZ2V0LXBldHMiLCJwb3N0LWFwcG9pbnRtZW50cyIsInBvc3Qtb3duZXJzIiwicG9zdC1wZXRzIiwicHV0LWFwcG9pbnRtZW50cyIsInB1dC1vd25lcnMiLCJwdXQtcGV0cyJdfQ.aE7p99vB8_wgtp_C_6Bnv5JMG1PmBN3zIvHfka7A8-L9Y27RFKhEsrogNBgo973cD4Yf9_6uRYD2h4qvDF7It6kBbFZgLwyYWP6FSc533Pyq_jg2KANi9h9skJBq-pxMYgbnxC3oNawX5svVqE7QsDwuAEuJe6XSuioXP4aumueGmqqpqobq7P9NCH68gX5A2EUZyHauRfEQFiPeLZDV8hIisyYJApViW58oZStsC_LkGChSv-m3_-tFbZyhGUCEl1HYDp4v-eb-HjOX9lTNEufP8WuQinZfowAeopXuR47VlBkFmOS6Qfy5kVww4nvBXZ-9mofRbMUDThxRbkUDuA'
}


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


class OwnerEndpoints(unittest.TestCase):

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

        res = self.client().get('/owners', headers=vet_tech_header)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        owners = data['owners']
        self.assertEqual(len(owners), 1)
        self.assertEqual(owners[0], {'id': 1, 'name': 'Bob', 'phone': '321-456-0987'})

    def test_get_owners__no_owners_in_database__returns_404_error(self):
        res = self.client().get('/owners', headers=vet_tech_header)

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('No owners found'), actual_response)

    def test_get_owner__returns_owner_with_matching_id(self):
        with self.app.app_context():
            Owner('Who dat?', "111-222-0000").insert()
            Owner('Jim', "222-222-2222").insert()

        res = self.client().get('/owners/2', headers=vet_tech_header)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        owner = data['owner']
        self.assertEqual(owner, {'name': 'Jim', 'phone': '222-222-2222', 'id': 2})

    def test_get_owners__owner_not_in_database__returns_404_error(self):
        res = self.client().get('/owners/100', headers=vet_tech_header)

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('Owner not found'), actual_response)

    def test_add_owner__adds_new_owner_to_database(self):

        request_body = {
            'name': "Dude",
            'phone': '111-222-3333'
        }

        post_res = self.client().post('/owners', json=request_body,  headers=vet_tech_header)

        self.assertEqual(post_res.status_code, 204)

        res = self.client().get('/owners', headers=vet_tech_header)
        data = json.loads(res.data)
        owners = data['owners']
        self.assertEqual(owners[0], {'name': request_body['name'],
                                     'id': 1,
                                     'phone': request_body['phone']})

    def test_add_owner__add_a_owner_that_without_a_name__return_a_422(self):

        request_body = {
            'phone': '321-654-0987'
        }

        post_res = self.client().post('/owners', json={
            'phone': '321-654-0987'
        }, headers=vet_tech_header)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Owner must have a name'), actual_response)

    def test_add_owner__add_a_owner_that_without_a_phone_number__return_a_422(self):

        request_body = {
            'name': 'No phone'
        }

        post_res = self.client().post('/owners', json=request_body, headers=vet_tech_header)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Owner must have a phone number'), actual_response)

    def test_update_owner__new_name_is_passed_in__updates_owner(self):
        with self.app.app_context():
            Owner('Jim', "222-222-2222").insert()

        res = self.client().put('/owners/1', json={'name': 'I am new owner name'}, headers=vet_tech_header)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/owners/1', headers=vet_tech_header)

        data = json.loads(res.data)
        owner = data['owner']
        self.assertEqual(owner, {'name': 'I am new owner name', 'phone': '222-222-2222', 'id': 1})

    def test_update_owner__new_phone_number_is_passed_in__updates_owner(self):
        with self.app.app_context():
            Owner('Jim', "222-222-2222").insert()

        res = self.client().put('/owners/1', json={'phone': '098-765-4321'}, headers=vet_tech_header)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/owners/1', headers=vet_tech_header)

        data = json.loads(res.data)
        owner = data['owner']
        self.assertEqual(owner, {'name': 'Jim', 'phone': '098-765-4321', 'id': 1})

    def test_update_owner__updating_owner_not_in_database__returns_404_error(self):
        res = self.client().put('/owners/400', json={'name': 'No owner here'}, headers=vet_tech_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not update, owner does not exist'), actual_response)

    def test_update_owner__no_request_body__returns_422_error(self):
        res = self.client().put('/owners/1', headers=vet_tech_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Request missing body'), actual_response)

    def test_update_owner__no_update_data_passed_in__returns_422_error(self):
        res = self.client().put('/owners/1', json={}, headers=vet_tech_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Must include a value to update'), actual_response)

    def test_delete_owner__deletes_owner_from_database(self):
        with self.app.app_context():
            Owner('who', '111-111-1111').insert()
            Owner('Doggo Owner', '444-444-4444').insert()

        res = self.client().get('/owners', headers=vet_manager_header)
        data = json.loads(res.data)
        self.assertEqual(2, len(data['owners']))

        res = self.client().delete('/owners/2', headers=vet_manager_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/owners', headers=vet_manager_header)
        data = json.loads(res.data)
        self.assertEqual(1, len(data['owners']))

        res = self.client().get('/owners/2', headers=vet_manager_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Owner not found'), actual_response)

    def test_delete_owner__owner_not_in_database__returns_404_error(self):
        res = self.client().delete('/owners/400000', headers=vet_manager_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not delete, owner does not exist'), actual_response)

    def test_delete_owner__caller_does_not_have_permission_to_delete__returns_403_error(self):
        res = self.client().delete('/owners/400000', headers=vet_tech_header)
        self.assertEqual(res.status_code, 403)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
