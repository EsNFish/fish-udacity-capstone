from flask import Flask, jsonify, abort, request

from models import setup_db, Owner, Pet, Appointment
from flask_migrate import Migrate
from flask_cors import CORS
from auth import requires_auth

def create_app(test_config=None):
    app = Flask(__name__)
    db = setup_db(app)

    CORS(app, resources={r"*": {"origins": "*"}})
    migrate = Migrate(app, db)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE')
        return response

    @app.route('/owners', methods=['GET', 'POST'])
    @requires_auth(['get-owners', 'post-owners'])
    def get_owners(auth_token):

        if request.method == 'GET':
            owners = Owner.query.all()

            if len(owners) == 0:
                abort(404, {'message': 'No owners found'})
            formatted_owners = [owner.format() for owner in owners]
            return jsonify({
                'success': True,
                'owners': formatted_owners
            }), 200

        if request.method == 'POST':
            owner_data = request.json

            if 'name' not in owner_data:
                abort(422, {'message': 'Owner must have a name'})
            if 'phone' not in owner_data:
                abort(422, {'message': 'Owner must have a phone number'})
            new_owner = Owner(owner_data['name'], owner_data['phone'])
            new_owner.insert()
            return jsonify({
                'success': True
            }), 204

    @app.route('/owners/<owner_id>', methods=['GET', 'PUT', 'DELETE'])
    @requires_auth(['get-owners', 'put-owners', 'delete-owners'])
    def handle_owner(auth_token, owner_id):
        if request.method == 'GET':
            owner = Owner.query.filter_by(id=owner_id).first()
            if owner is None:
                abort(404, {'message': 'Owner not found'})
            return jsonify({
                'success': True,
                'owner': owner.format()
            }), 200
        if request.method == 'PUT':
            update_data = request.json

            if update_data is None:
                abort(422, {'message': 'Request missing body'})
            if 'name' not in update_data and 'phone' not in update_data:
                abort(422, {'message': 'Must include a value to update'})

            owner = Owner.query.filter_by(id=owner_id).first()

            if owner is None:
                abort(404, {'message': 'Can not update, owner does not exist'})
            if 'name' in update_data:
                owner.name = update_data['name']
            if 'phone' in update_data:
                owner.phone = update_data['phone']

            owner.update()

            return jsonify({
                'success': True,
            }), 200

        if request.method == 'DELETE':
            '''
            adding this to handle one edge case
            '''
            if 'delete-owners' not in auth_token['permissions']:
                abort(403, {'message': "Missing delete permission"})

            owner = Owner.query.filter_by(id=owner_id).first()

            if owner is None:
                abort(404, {'message': 'Can not delete, owner does not exist'})

            owner.delete()

            return jsonify({
                'success': True,
            }), 200

    @app.route('/pets', methods=['GET', 'POST'])
    @requires_auth(['get-pets', 'post-pets'])
    def get_pets(auth_token):

        if request.method == 'GET':
            pets = Pet.query.all()

            if len(pets) == 0:
                abort(404, {'message': 'No pets found'})
            formatted_pets = [pet.format() for pet in pets]
            return jsonify({
                'success': True,
                'pets': formatted_pets
            }), 200

        if request.method == 'POST':
            pet_data = request.json

            if 'name' not in pet_data:
                abort(422, {'message': 'Pet must have a name'})
            if 'species' not in pet_data:
                abort(422, {'message': 'Pet must have a species'})
            new_pet = Pet(pet_data['name'], pet_data['species'], pet_data['breed'])
            new_pet.insert()
            return jsonify({
                'success': True
            }), 204

    @app.route('/pets/<pet_id>', methods=['GET', 'PUT', 'DELETE'])
    @requires_auth(['get-pets', 'put-pets', 'delete-pets'])
    def handle_pet(auth_token, pet_id):
        if request.method == 'GET':
            pet = Pet.query.filter_by(id=pet_id).first()
            if pet is None:
                abort(404, {'message': 'Pet not found'})
            return jsonify({
                'success': True,
                'pet': pet.format()
            }), 200
        if request.method == 'PUT':
            update_data = request.json

            if update_data is None:
                abort(422, {'message': 'Request missing body'})
            if 'name' not in update_data and 'species' not in update_data and 'breed' not in update_data:
                abort(422, {'message': 'Must include a value to update'})

            pet = Pet.query.filter_by(id=pet_id).first()

            if pet is None:
                abort(404, {'message': 'Can not update, pet does not exist'})
            if 'name' in update_data:
                pet.name = update_data['name']
            if 'species' in update_data:
                pet.species = update_data['species']
            if 'breed' in update_data:
                pet.breed = update_data['breed']

            pet.update()

            return jsonify({
                'success': True,
            }), 200

        if request.method == 'DELETE':

            '''
                adding this to handle one edge case
            '''
            if 'delete-owners' not in auth_token['permissions']:
                abort(403, {'message': "Missing delete permission"})

            pet = Pet.query.filter_by(id=pet_id).first()

            if pet is None:
                abort(404, {'message': 'Can not delete, pet does not exist'})

            pet.delete()

            return jsonify({
                'success': True,
            }), 200

    @app.route('/appointments', methods=['GET', 'POST'])
    @requires_auth(['get-appointments', 'post-appointments'])
    def get_appointments(auth_token):

        if request.method == 'GET':
            appointments = Appointment.query.all()

            if len(appointments) == 0:
                abort(404, {'message': 'No appointments found'})
            formatted_appointments = [appointment.format() for appointment in appointments]
            return jsonify({
                'success': True,
                'appointments': formatted_appointments
            }), 200

        if request.method == 'POST':
            appointment_data = request.json

            if 'date' not in appointment_data:
                abort(422, {'message': 'Appointment must have a date'})
            if 'time' not in appointment_data:
                abort(422, {'message': 'Appointment must have a time'})
            if 'pet_id' not in appointment_data:
                abort(422, {'message': 'Appointment must have a pet'})
            if 'owner_id' not in appointment_data:
                abort(422, {'message': 'Appointment must have an owner'})

            new_appointment = Appointment(appointment_data['date'], appointment_data['time'], appointment_data['pet_id'], appointment_data['owner_id'])

            new_appointment.insert()

            return jsonify({
                'success': True
            }), 204

    @app.route('/appointments/<appointment_id>', methods=['GET', 'PUT', 'DELETE'])
    @requires_auth(['get-appointments', 'put-appointments', 'delete-appointments'])
    def handle_appointment(auth_token, appointment_id):
        if request.method == 'GET':
            appointment = Appointment.query.filter_by(id=appointment_id).first()
            if appointment is None:
                abort(404, {'message': 'Appointment not found'})
            return jsonify({
                'success': True,
                'appointment': appointment.format()
            }), 200
        if request.method == 'PUT':
            update_data = request.json

            if update_data is None:
                abort(422, {'message': 'Request missing body'})
            if 'time' not in update_data and 'date' not in update_data:
                abort(422, {'message': 'Must include a value to update'})

            appointment = Appointment.query.filter_by(id=appointment_id).first()

            if appointment is None:
                abort(404, {'message': 'Can not update, appointment does not exist'})
            if 'time' in update_data:
                appointment.time = update_data['time']
            if 'date' in update_data:
                appointment.date = update_data['date']

            appointment.update()

            return jsonify({
                'success': True,
            }), 200

        if request.method == 'DELETE':
            '''
               adding this to handle one edge case
            '''
            if 'delete-appointments' not in auth_token['permissions']:
                abort(403, {'message': "Missing delete permission"})

            appointment = Appointment.query.filter_by(id=appointment_id).first()

            if appointment is None:
                abort(404, {'message': 'Can not delete, appointment does not exist'})

            appointment.delete()

            return jsonify({
                'success': True,
            }), 200


    @app.errorhandler(404)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": error.description['message']
        })

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": error.description['message']
        })

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
