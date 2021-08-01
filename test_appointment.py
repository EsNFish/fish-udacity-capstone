import json
import unittest

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text as sa_text

from app import create_app
from models import setup_db, Appointment, Pet, Owner


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

        res = self.client().get('/appointments')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        appointments = data['appointments']
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0], {'id': 1, 'pet_id': 1, 'owner_id': 1, 'time': '10:00', 'date': '12/12/2021'})

    def test_get_appointments__no_appointments_in_database__returns_404_error(self):
        res = self.client().get('/appointments')

        actual_response = json.loads(res.data)

        self.assertEqual(expected_404_builder('No appointments found'), actual_response)

    def test_get_appointment__returns_appointment_with_matching_id(self):
        with self.app.app_context():
            Pet('Fifi', "dog", 'pug').insert()
            Owner('Bob Ross', '122-344-5666').insert()
            Appointment('12/12/2021', '10:00', 1, 1).insert()
            Appointment('1/10/2022', '10:00', 1, 1).insert()

        res = self.client().get('/appointments/2')

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        appointment = data['appointment']
        self.assertEqual(appointment, {'id': 2, 'pet_id': 1, 'owner_id': 1, 'time': '10:00', 'date': '1/10/2022'})

    def test_get_appointment__appointment_not_in_database__returns_404_error(self):
        res = self.client().get('/appointments/100')

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

        post_res = self.client().post('/appointments', json=request_body)

        self.assertEqual(post_res.status_code, 204)

        res = self.client().get('/appointments')
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

        post_res = self.client().post('/appointments', json=request_body)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Appointment must have a time'), actual_response)

    def test_add_appointment__add_a_appointment_that_without_a_date__return_a_422(self):

        request_body = {
            'time': '10:00',
            'pet_id': 1,
            'owner_id': 1
        }

        post_res = self.client().post('/appointments', json=request_body)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Appointment must have a date'), actual_response)

    def test_add_appointment__add_a_appointment_that_without_a_pet_id__return_a_422(self):

        request_body = {
            'time': '10:00',
            'date': '1/1/2022',
            'owner_id': 1
        }

        post_res = self.client().post('/appointments', json=request_body)

        actual_response = json.loads(post_res.data)

        self.assertEqual(expected_422_builder('Appointment must have a pet'), actual_response)

    def test_add_appointment__add_a_appointment_that_without_a_owner_id__return_a_422(self):

        request_body = {
            'time': '10:00',
            'date': '1/1/2022',
            'pet_id': 1
        }

        post_res = self.client().post('/appointments', json=request_body)

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
        })

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/appointments/1')

        data = json.loads(res.data)
        appointment = data['appointment']
        self.assertEqual(appointment, {'date': '1/1/2022',
                                       'time': "11:00",
                                       'id': 1,
                                       'owner_id': 1,
                                       'pet_id': 1})

    def test_update_appointment__updating_appointment_not_in_database__returns_404_error(self):
        res = self.client().put('/appointments/400', json={'time': '2:00'})
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not update, appointment does not exist'), actual_response)

    def test_update_appointment__no_request_body__returns_422_error(self):
        res = self.client().put('/appointments/1')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Request missing body'), actual_response)

    def test_update_appointment__no_update_data_passed_in__returns_422_error(self):
        res = self.client().put('/appointments/1', json={})
        actual_response = json.loads(res.data)
        self.assertEqual(expected_422_builder('Must include a value to update'), actual_response)

    def test_delete_appointment__deletes_appointment_from_database(self):
        with self.app.app_context():
            Pet('Fifi', "dog", 'pug').insert()
            Owner('Bob Ross', '122-344-5666').insert()
            Appointment('12/12/2021', '10:00', 1, 1).insert()
            Appointment('1/10/2022', '10:00', 1, 1).insert()

        res = self.client().get('/appointments')
        data = json.loads(res.data)
        self.assertEqual(2, len(data['appointments']))

        res = self.client().delete('/appointments/2')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

        res = self.client().get('/appointments')
        data = json.loads(res.data)
        self.assertEqual(1, len(data['appointments']))

        res = self.client().get('/appointments/2')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Appointment not found'), actual_response)

    def test_delete_appointment__appointment_not_in_database__returns_404_error(self):
        res = self.client().delete('/appointments/400000')
        actual_response = json.loads(res.data)
        self.assertEqual(expected_404_builder('Can not delete, appointment does not exist'), actual_response)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
