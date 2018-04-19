from flask import Flask
import json
import logging
import re
from flask_ask import Ask, statement, question, session
from os import listdir
import random

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


def get_lyric(file):
    return open(file, 'r').read().split('\n')


@ask.launch
def start_game():
    session.attributes['counter'] = 0
    session.attributes['win_counter'] = 0
    session.attributes['game_state'] = False
    return question("Welcome to the Lyrics Game. I will say the first two lines of a song and you will have to say the next line. Would you like to play?")


@ask.intent('AMAZON.YesIntent')
def say_yes():
    if session.attributes['game_state']:
        return answer("Yes")
    session.attributes['game_state'] = True
    file = "data/"+random_song()
    lyric = get_lyric(file)
    session.attributes['correct_lyric'] = lyric[2]
    return question('<speak> Get ready! <break time ="1s"/>' + lyric[0] + '<break time="500ms"/> ' + lyric[1]+ '</speak>')


def random_song():
    lyrics_list = [lyrics for lyrics in listdir("data/") if lyrics.endswith(".txt")]
    return random.choice(lyrics_list)


@ask.intent('AMAZON.NoIntent')
def say_no():
    if session.attributes['game_state']:
        return answer("No")
    win_counter = session.attributes['win_counter']
    counter = session.attributes['counter']
    if counter > 0:
        return statement("Thanks for playing. You got " + str(win_counter) + " out of " + str(counter) + " correct!")
    return statement('<speak> Goodbye. <amazon:effect name="whispered"> Why did you start the game then?</amazon:effect>. </speak>')


@ask.intent('AnswerIntent')
def answer(lyric):
    if not session.attributes['game_state']:
        return question("Sorry, I didn't get that. Would you like to play another round?")
    session.attributes['game_state'] = False
    correct_lyric = session.attributes['correct_lyric']
    session.attributes['counter'] += 1

    if compare_lyric(lyric, correct_lyric):
        session.attributes['win_counter'] += 1
        return question("Correct. Would you like to play another round?")

    return question("Incorrect. The lyrics were " + correct_lyric + ". Would you like to play another round?")





def sanitise(lyric):
    lyric = re.sub(r'[\s]', ' ', lyric)
    lyric_sanitise = re.sub(r'[^\w\s]', '', lyric)
    return lyric_sanitise.lower()


def compare_lyric(user_lyric, correct_lyric):
    user_lyric_list = sanitise(user_lyric).split(' ')
    correct_lyric_list = sanitise(correct_lyric).split(' ')

    if len(user_lyric_list)/len(correct_lyric_list) > 0.5:
        correct_counter = 0
        for word in user_lyric_list:
            if word in correct_lyric_list:
                correct_counter += 1
        return correct_counter/len(correct_lyric_list) >= 0.65
    return False


if __name__ == '__main__':
    app.run(debug=True)

