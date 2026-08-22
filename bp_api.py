from calendar import error

from flask import Flask, render_template, request, Blueprint, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from models import Server, Player, db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/server', methods=['GET'])
def get_server_data():
    server_id = session.get('connected_server') or request.get_json().get('id')
    server = Server.query.get(server_id)
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

@bp.route('/submit-vote', methods=['POST'])
def submit_vote():
    data = request.get_json()
    player_id = data.get('player_id')
    poem_index = data.get('poem_index')

    player = Player.query.get(player_id)
    if player:
        player.set_vote(poem_index)
        db.session.commit()
        return {'message': 'Vote submitted successfully!'}
    else:
        print("Player not found")
        return {'message': 'Player not found.'}, 404


@bp.route('/join_game', methods=['POST'])
def join_game():
    data = request.form
    join_code = str(data.get('code'))
    server = Server.query.filter_by(code=join_code).first()
    if not server:
        flash("Invalid join code", "error")
        return redirect(url_for('room_join'))
    player_name = data.get('name')

    if player_name:
        player = Player(name=player_name, server=server.id)
        db.session.add(player)
        db.session.commit()
        session['connected_server'] = server.id
        session['player'] = player.id
        return redirect(url_for('game'))
    else:
        flash("Player name is required", "error")
        return redirect(url_for('room_join'))