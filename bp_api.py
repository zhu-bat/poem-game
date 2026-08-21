from flask import Flask, render_template, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/server', methods=['GET'])
def get_server_data():
    server = Server.query.first()
    if server:
        return server.to_json()
    else:
        return {}

@bp.route('/submit-poem', methods=['POST'])
def submit_poem():
    data = request.get_json()
    player_id = data.get('player_id')
    poem = data.get('poem')

    player = Player.query.get(player_id)
    if player:
        player.set_poem(poem)
        db.session.commit()
        return {'message': 'Poem submitted successfully!'}
    else:
        return {'message': 'Player not found.'}, 404


@bp.route('/join_game', methods=['POST'])
def join_game():
    data = request.form
    join_code = data.get('join_code')
    server = Server.query.first()
    if not server:
        return {'message': 'Invalid join code.'}, 400
    player_name = data.get('player_name')

    if player_name:
        player = Player(name=player_name, server=server.id)
        db.session.add(player)
        db.session.commit()
        return {'message': 'Player joined successfully!', 'player_id': player.id}
    else:
        return {'message': 'Player name is required.'}, 400