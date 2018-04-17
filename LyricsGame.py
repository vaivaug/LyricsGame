from flask import Flask, abort
import json
from flask_ask import Ask, delegate, statement

app = Flask(__name__)
ask = Ask(app, '/')


def getLyrics(file):
    data = json.load(open(file))
    lyrics = data['message']['body']['lyrics']['lyrics_body'].split('\n')
    return lyrics[:-3]

@ask.intent('StartGame')
def start_game():
    file = "data/taylor-swift-lyrics.json"

    lyrics = getLyrics(file)
    print(lyrics)
    return statement(lyrics[0]+'\n'+lyrics[1])

if __name__ == '__main__':
    app.run(debug=True)

