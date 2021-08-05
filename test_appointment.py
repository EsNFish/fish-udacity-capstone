import json
import unittest

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text as sa_text

from app import create_app
from models import setup_db, Appointment, Pet, Owner


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


class AppointmentsEndpoints(unittest.TestCase):

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
                    sa_text('''TRUNCATE TABLE appointments RESTART IDENTITY CASCADE ''').execution_options(
                        autocommit=True))
                self.db.engine.execute(
                    sa_text('''TRUNCATE TABLE pets RESTART IDENTITY CASCADE ''').execution_options(
                        autocommit=True))
                self.db.engine.execute(
                    sa_text('''TRUNCATE TABLE appointments RESTART IDENTITY CASCADE ''').execution_options(
                        autocommit=True))
            except:
                self.db.session.rollback()

    '''
    Appointments Tests
    '''

    def test_get_appointments__returns_appointments(self):
        Pet('Fifi', "dog", 'pug').insert()
        Owner('Bob Ross', '122-344-5666').insert()
        Appointment('12/12/2021', '10:00', 1, 1).insert()

        res = self.client().get('/appointments', headers=vet_tech_header)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        appointments = data['appointments']
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0], {'id': 1, 'pet_id': 1, 'owner_id': 1, 'time': '10:00', 'date': '12/12/2021'})

    def test_get_appointments__no_appointments_in_database__returns_404_error(self):
        res = self.client().get('/appointments', headers=vet_tech_header)

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('No appointments found'), actual_response)

    def test_get_appointment__returns_appointment_with_matching_id(self):
        with self.app.app_context():
            Pet('Fifi', "dog", 'pug').insert()
            Owner('Bob Ross', '122-344-5666').insert()
            Appointment('12/12/2021', '10:00', 1, 1).insert()
            Appointment('1/10/2022', '10:00', 1, 1).insert()

        res = self.client().get('/appointments/2', headers=vet_tech_header)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        appointment = data['appointment']
        self.assertEqual(appointment, {'id': 2, 'pet_id': 1, 'owner_id': 1, 'time': '10:00', 'date': '1/10/2022'})

    def test_get_appointment__appointment_not_in_database__returns_404_error(self):
        res = self.client().get('/appointments/100', headers=vet_tech_header)

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('Appointment not found'), actual_response)

    def test_add_appointment__adds_new_appointment_to_database(self):

        Pet('Fifi', "dog", 'pug').insert()
        Owner('Bob Ross', '122-344-5666').insert()

        request_body = {
            'time': "10:00",
            'date': '1/1/2022',
            'pet_id': 1,
            'owner_id': 1
        }

        post_res = self.client().post('/appointments', json=request_body, headers=vet_tech_header)

        self.assertEqual(post_res.status_code, 204)

        res = self.client().get('/appointments', headers=vet_tech_header)
        data = json.loads(res.data)
        appointments = data['appointments']
        self.assertEqual(appointments[0], {'date': request_body['date'],
                                           'time': request_body['time'],
                                           'id': 1,
                                           'owner_id': request_body['owner_id'],
                                           'pet_id': request_body['pet_id']})

    def test_add_appointment__add_a_appointment_that_without_a_time__return_a_422(self):

        request_body = {
            'date': '1/1/2022',
            'pet_id': 1,
            'owner_id': 1
        }

        post_res = self.client().post('/appointments', json=request_body, headers=vet_tech_header)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Appointment must have a time'), actual_response)

    def test_add_appointment__add_a_appointment_that_without_a_date__return_a_422(self):

        request_body = {
            'time': '10:00',
            'pet_id': 1,
            'owner_id': 1
        }

        post_res = self.client().post('/appointments', json=request_body, headers=vet_tech_header)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Appointment must have a date'), actual_response)

    def test_add_appointment__add_a_appointment_that_without_a_pet_id__return_a_422(self):

        request_body = {
            'time': '10:00',
            'date': '1/1/2022',
            'owner_id': 1
        }

        post_res = self.client().post('/appointments', json=request_body, headers=vet_tech_header)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Appointment must have a pet'), actual_response)

    def test_add_appointment__add_a_appointment_that_without_a_owner_id__return_a_422(self):

        request_body = {
            'time': '10:00',
            'date': '1/1/2022',
            'pet_id': 1
        }

        post_res = self.client().post('/appointments', json=request_body, headers=vet_tech_header)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Appointment must have an owner'), actual_response)

    def test_update_appointment__new_values_passed_in__only_date_and_time_are_updated(self):
        with self.app.app_context():
            Pet('Fifi', "dog", 'pug').insert()
            Owner('Bob Ross', '122-344-5666').insert()
            Appointment('12/12/2021', '10:00', 1, 1).insert()

        res = self.client().put('/appointments/1', json={
            'time': "11:00",
            'date': '1/1/2022',
            'pet_id': 2,
            'owner_id': 2
        }, headers=vet_tech_header)

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/appointments/1', headers=vet_tech_header)

        data = json.loads(res.data)
        appointment = data['appointment']
        self.assertEqual(appointment, {'date': '1/1/2022',
                                       'time': "11:00",
                                       'id': 1,
                                       'owner_id': 1,
                                       'pet_id': 1})

    def test_update_appointment__updating_appointment_not_in_database__returns_404_error(self):
        res = self.client().put('/appointments/400', json={'time': '2:00'}, headers=vet_tech_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not update, appointment does not exist'), actual_response)

    def test_update_appointment__no_request_body__returns_422_error(self):
        res = self.client().put('/appointments/1', headers=vet_tech_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Request missing body'), actual_response)

    def test_update_appointment__no_update_data_passed_in__returns_422_error(self):
        res = self.client().put('/appointments/1', json={}, headers=vet_tech_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Must include a value to update'), actual_response)

    def test_delete_appointment__deletes_appointment_from_database(self):
        with self.app.app_context():
            Pet('Fifi', "dog", 'pug').insert()
            Owner('Bob Ross', '122-344-5666').insert()
            Appointment('12/12/2021', '10:00', 1, 1).insert()
            Appointment('1/10/2022', '10:00', 1, 1).insert()

        res = self.client().get('/appointments', headers=vet_manager_header)
        data = json.loads(res.data)
        self.assertEqual(2, len(data['appointments']))

        res = self.client().delete('/appointments/2', headers=vet_manager_header)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/appointments', headers=vet_manager_header)
        data = json.loads(res.data)
        self.assertEqual(1, len(data['appointments']))

        res = self.client().get('/appointments/2', headers=vet_manager_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Appointment not found'), actual_response)

    def test_delete_appointment__appointment_not_in_database__returns_404_error(self):
        res = self.client().delete('/appointments/400000', headers=vet_manager_header)
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not delete, appointment does not exist'), actual_response)

    def test_delete_appointment__caller_does_not_have_permission_to_delete__returns_403_error(self):
        res = self.client().delete('/appointments/400000', headers=vet_tech_header)
        self.assertEqual(res.status_code, 403)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
