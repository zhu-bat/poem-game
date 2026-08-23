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

    if not poem or len(poem) < 3:
        return {'message': 'Poem must be at least 3 characters long.'}, 400

    player = Player.query.get(player_id)
    if player and poem:
        player.set_poem(poem)
        db.session.commit()
        return {'message': 'Poem submitted successfully!'}
    else:
        return {'message': 'Player not found.'}, 404

@bp.route('/submit-vote', methods=['POST'])
def submit_vote():
    player_id = session.get('player')
    if not player_id:
        return abort(400, description="No player in session.")
    player = Player.query.get(player_id)
    if not player:
        return abort(400, description="Invalid player.")

    data = request.get_json()
    poem_index = data.get('poem_index')

    player.set_vote(poem_index)
    db.session.commit()
    return {'message': 'Vote submitted successfully!'}

@bp.route('/join_game', methods=['POST'])
def join_game():
    data = request.form
    join_code = str(data.get('code'))
    server = Server.query.filter_by(code=join_code).first()
    if not server:
        flash("Invalid join code", "error")
        return redirect(url_for('room_join', code=join_code))
    player_name = data.get('name')


    if not player_name:
        flash("Player name is required", "error")
        return redirect(url_for('room_join', code=join_code))
    if len(player_name) < 3 or len(player_name) > 20:
        flash("Player name must be at least 3 characters and at most 20 characters long", "error")
        return redirect(url_for('room_join', code=join_code))
    all_player_names = [p.name for p in server.get_players()]
    if player_name in all_player_names:
        flash("Player name already taken", "error")
        return redirect(url_for('room_join', code=join_code))
    player = Player(name=player_name, server=server.id)
    db.session.add(player)
    db.session.commit()
    server.get_vip()
    session['connected_server'] = server.id
    session['player'] = player.id
    return redirect(url_for('game'))


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
    # is_vip = player.is_vip()
    # if not is_vip:
    #     return abort(403, description="Only the VIP can start the game.")
    if server.phase not in {"pregame", "results"}:
        return abort(400, description="Game has already started.")
    server.clear_round()
    return redirect(url_for('game'))