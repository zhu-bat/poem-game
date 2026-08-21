
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poem_game.db'
app.secret_key = 'thisisagoodsecretkey'
db = SQLAlchemy(app)

from models import Server, Player

with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/words-test')
def words_test():
    return render_template('words_test.html')

@app.route('/api')
def get_server_data():
    server = Server.query.first()
    if server:
        return server.to_json()
    else:
        return {}


@app.route('/submit-poem', methods=['POST'])
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
