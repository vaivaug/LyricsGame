from flask import Flask, abort
from flask_ask import Ask, delegate, statement

app = Flask(__name__)
ask = Ask(app, '/')

@ask.intent('StartGame')
def start_game():
    return

if __name__ == '__main__':
    app.run(debug=True)