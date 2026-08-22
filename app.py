from flask import render_template, url_for, redirect, session, request

from bp_api import bp as bp_api
from models import app, db, Server, Player


app.register_blueprint(bp_api)


@app.route('/')
def title_screen():  # put application's code here
    return render_template('title_screen.html')


@app.route('/join')
def room_join():
    chode = request.args.get('code')
    return render_template('player/room_join.html', code=chode)


@app.route('/words-test')
def words_test():
    return render_template('player/words_test.html')


@app.route('/create')
def create():
    server = Server()
    server.set_phase("pregame")
    db.session.add(server)
    db.session.commit()
    return redirect(url_for('room_join', code=server.code))


@app.route('/game')
def game():
    connected_server = session.get('connected_server')
    player_id = session.get('player')
    if not connected_server or not player_id:
        return redirect(url_for('room_join'))
    server = Server.query.get(connected_server)
    player = Player.query.get(player_id)
    if not server or not player:
        return redirect(url_for('room_join'))

    server.get_vip()
    is_vip = player.is_vip()
    if is_vip:
        if server.phase == "writing" and server.all_poems_submitted():
            server.set_phase("voting")
            db.session.commit()
        if server.phase == "voting" and server.all_votes_submitted():
            server.set_phase("results")
            db.session.commit()

    if server.phase == "pregame":
        return render_template('player/pregame_waiting.html', player=player_id, server=server, is_vip=is_vip)
    if server.phase == "writing" and not player.poem_submitted():
        return render_template('player/words_test.html', player=player_id)
    if server.phase == "writing":
        return render_template("player/ingame_waiting.html", phase="voting")
    if server.phase == "voting" and not player.vote_submitted():
        return render_template("player/voting_test.html", player=player_id)
    if server.phase == "voting":
        return render_template("player/ingame_waiting.html", phase="results")
    if server.phase == "results":
        server.update_score()
        return render_template("player/results.html", player=player_id, server=server, is_vip=is_vip)
    return render_template('game.html', server=server.to_json())


@app.route('/clear')
def clear():
    session.clear()
    return redirect(url_for('room_join'))


@app.route('/bussy')
def bussy():
    server = Server()
    db.session.add(server)
    db.session.commit()
    bussy = Player(name='Bussy', server=server.id)
    db.session.add(bussy)
    # server.add_player(bussy)
    zubat = Player(name='Zubat', server=server.id)
    db.session.add(zubat)
    # server.add_player(zubat)
    db.session.commit()

    return server.to_json()


if __name__ == '__main__':
    app.run()
