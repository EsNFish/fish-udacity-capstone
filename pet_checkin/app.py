from flask import Flask, jsonify, abort, request

from models import setup_db, Owner
from flask_migrate import Migrate
from flask_cors import CORS


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
    def get_owners():

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
    def handle_owner(owner_id):
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
            owner = Owner.query.filter_by(id=owner_id).first()

            if owner is None:
                abort(404, {'message': 'Can not delete, owner does not exist'})

            owner.delete()

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


if __name__ == '__main__':
    create_app().run()
