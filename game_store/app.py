from flask import Flask, jsonify, abort, request

from .models import setup_db, Game
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


# if __name__ == '__main__':
#     create_app().run()
