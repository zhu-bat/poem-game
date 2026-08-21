from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/words-test')
def words_test():  # put application's code here
    return render_template('words_test.html', words=["hello", "world", "test", "."])


if __name__ == '__main__':
    app.run()
