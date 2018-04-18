from flask import Flask
import json
import logging
import re
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


def getLyrics(file):
    data = json.load(open(file))
    lyrics = data['message']['body']['lyrics']['lyrics_body'].split('\n')
    return lyrics[:-3]


@ask.launch
def start_game():
    session.attributes['counter'] = 0
    session.attributes['win_counter'] = 0
    return question("Welcome to the Lyrics Game. I will say the first two lines of a song and you will have to say the next line. Would you like to play?")


@ask.intent('AMAZON.YesIntent')
def say_yes():
    file = "data/gotye-lyrics.json"
    lyrics = getLyrics(file)
    session.attributes['correct_lyrics'] = lyrics[2]
    return question('<speak> Get ready! <break time ="1s"/>' + lyrics[0] + '<break time="500ms"/> ' + lyrics[1]+ '</speak>')


@ask.intent('AMAZON.NoIntent')
def say_no():
    win_counter = session.attributes['win_counter']
    counter = session.attributes['counter']
    if counter > 0:
        return statement("Thanks for playing. You got " + str(win_counter) + " out of " + str(counter) + " correct!")
    return statement('<speak> Goodbye. <amazon:effect name="whispered"> Why did you start the game then?</amazon:effect>. </speak>')


@ask.intent('AnswerIntent')
def answer(lyric):
    sanitised_correct_lyric = sanitise(session.attributes['correct_lyrics'])
    sanitised_guessed_lyric = sanitise(lyric)
    session.attributes['counter'] += 1

    if sanitised_correct_lyric == sanitised_guessed_lyric:
        session.attributes['win_counter'] += 1
        return question("Correct. Would you like to play another round?")

    return question("Incorrect. The lyrics were " + session.attributes['correct_lyrics'] + ". Would you like to play another round?")


def sanitise(text):
    normal_text = re.sub(r'[^\w]', '', text)
    return normal_text.lower()


if __name__ == '__main__':
    app.run(debug=True)

