from flask import request, Blueprint, session, redirect, url_for, flash, abort

from models import Server, Player, db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/server', methods=['GET'])
def get_server_data():
    server_id = session.get('connected_server')
    server = Server.query.get(server_id)
    if server:
        return server.to_json()
    else:
        return {}

@bp.route('/servers', methods=['GET'])
def get_all_servers_data():
    servers = Server.query.all()
    if servers:
        return {server.id: server.to_json() for server in servers}
    else:
        return {}

@bp.route('/poems', methods=['GET'])
def get_poem_data():
    connected_server = session.get('connected_server')
    player_id = session.get('player')
    if not connected_server or not player_id:
        return abort(400, description="No server or player in session.")
    server = Server.query.get(connected_server)
    player = Player.query.get(player_id)
    if not server or not player:
        return abort(400, description="Invalid server or player.")
    player.get_voting_poems(server)
    return {'poems': player.get_voting_poems(server)}

@bp.route('/words', methods=['GET'])
def get_words():
    connected_server = session.get('connected_server')
    player_id = session.get('player')
    if not connected_server or not player_id:
        return abort(400, description="No server or player in session.")
    server = Server.query.get(connected_server)
    player = Player.query.get(player_id)
    if not server or not player:
        return abort(400, description="Invalid server or player.")
    player.get_words(server)
    return {'words': player.get_words(server)}

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
        vip = server.get_vip()
        session['connected_server'] = server.id
        session['player'] = player.id
        return redirect(url_for('game'))
    else:
        flash("Player name is required", "error")
        return redirect(url_for('room_join'))


@bp.route('/continue-game')
def continue_game():
    connected_server = session.get('connected_server')
    player_id = session.get('player')
    if not connected_server or not player_id:
        return abort(400, description="No server or player in session.")
    server = Server.query.get(connected_server)
    player = Player.query.get(player_id)
    if not server or not player:
        return abort(400, description="Invalid server or player.")
    is_vip = player.is_vip()
    if not is_vip:
        return abort(403, description="Only the VIP can start the game.")
    if server.phase not in {"pregame", "results"}:
        return abort(400, description="Game has already started.")
    server.clear_round()
    return redirect(url_for('game'))