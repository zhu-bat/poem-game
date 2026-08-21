
from models import *
from flask import Flask, render_template

app = Flask(__name__)



@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/words-test')
def words_test():
    return render_template('words_test.html')


@app.route('/bussy')
def bussy():
    server = Server()
    bussy = Player('Bussy')
    server.add_player(bussy)
    zubat = Player('Zubat')
    server.add_player(zubat)

    return server.to_json()


if __name__ == '__main__':
    app.run()
