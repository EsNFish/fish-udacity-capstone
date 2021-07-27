from flask import Flask, jsonify, abort, request

from models import setup_db, Game
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

    @app.route('/games', methods=['GET', 'POST'])
    def get_games():

        if request.method == 'GET':
            games = Game.query.all()

            if len(games) == 0:
                abort(404, {'message': 'No games found'})
            formatted_games = [game.format() for game in games]
            return jsonify({
                'success': True,
                'games': formatted_games
            }), 200

        if request.method == 'POST':
            game_data = request.json

            if 'name' not in game_data:
                abort(422, {'message': 'Game must have a name'})
            new_game = Game(game_data['name'], game_data['genre'], game_data['console'])
            new_game.insert()
            return jsonify({
                'success': True
            }), 204

    @app.route('/games/<game_id>', methods=['GET', 'PUT', 'DELETE'])
    def handle_game(game_id):
        if request.method == 'GET':
            game = Game.query.filter_by(id=game_id).first()
            if game is None:
                abort(404, {'message': 'Game not found'})
            return jsonify({
                'success': True,
                'game': game.format()
            }), 200
        if request.method == 'PUT':
            update_data = request.json

            if update_data is None:
                abort(422, {'message': 'Request missing body'})
            if 'name' not in update_data and 'genre' not in update_data and 'console' not in update_data:
                abort(422, {'message': 'Must include a value to update'})

            game = Game.query.filter_by(id=game_id).first()

            if game is None:
                abort(404, {'message': 'Can not update, game does not exist'})
            if 'name' in update_data:
                game.name = update_data['name']
            if 'genre' in update_data:
                game.genre = update_data['genre']
            if 'console' in update_data:
                game.console = update_data['console']

            game.update()

            return jsonify({
                'success': True,
            }), 200

        if request.method == 'DELETE':
            game = Game.query.filter_by(id=game_id).first()

            if game is None:
                abort(404, {'message': 'Can not delete, game does not exist'})

            game.delete()

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
