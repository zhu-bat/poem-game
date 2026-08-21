
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from bp_api import bp as bp_api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poem_game.db'
app.secret_key = 'thisisagoodsecretkey'
db = SQLAlchemy(app)

app.register_blueprint(bp_api)

from models import Server, Player

with app.app_context():
    db.create_all()

@app.route('/')
def title_screen():  # put application's code here
    return render_template('title_screen.html')


@app.route('/join')
def room_join():
    return render_template('room_join.html')



@app.route('/words-test')
def words_test():
    return render_template('words_test.html')







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
