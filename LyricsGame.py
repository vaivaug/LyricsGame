from flask import Flask
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
    session.attributes['songs'] = [lyrics for lyrics in listdir("data/") if lyrics.endswith(".txt")]
    session.attributes['previous_response'] = "Welcome to the Lyrics Game. I will say lines of a song and you will have to say the next line. Would you like to play?"
    return question(session.attributes['previous_response'])


@ask.intent('AMAZON.HelpIntent')
def help_intent():
    session.attributes['previous_response'] = "This is the Lyrics Game. I will say lines of a song and you will have to say the next line. Would you like to play?"
    session.attributes['previous_response_type'] = "question"
    return question(session.attributes['previous_response'])


@ask.intent('AMAZON.YesIntent')
def say_yes():
    if session.attributes['game_state']:
        return answer("Yes")
    session.attributes['game_state'] = True
    file = "data/"+random_song()
    lyric = get_lyric(file)
    session.attributes['correct_lyric'] = lyric[2]
    session.attributes['song'] = lyric[3]
    session.attributes['artist'] = lyric[4]
    session.attributes['previous_response'] = '<speak> Get ready! <break time ="1s"/>' + lyric[0] + '<break time="500ms"/> ' + lyric[1]+ '</speak>'
    return question(session.attributes['previous_response'])


def random_song():
    current_song = random.choice(session.attributes['songs'])
    session.attributes['songs'].remove(current_song)
    return current_song


@ask.intent('AMAZON.CancelIntent')
@ask.intent('AMAZON.StopIntent')
@ask.intent('AMAZON.NoIntent')
def say_no():
    if session.attributes['game_state']:
        return answer("No")
    return end_game("")


def end_game(response):
    win_counter = session.attributes['win_counter']
    counter = session.attributes['counter']
    if counter > 0:
        return statement(response + "Thanks for playing. You got " + str(win_counter) + " out of " + str(counter) + " correct!")
    return statement('<speak> Goodbye. <prosody volume="soft"> Why did you start the game then?</prosody> </speak>')


@ask.intent('AnswerIntent')
def answer(lyric):
    if not session.attributes['game_state']:
        session.attributes['previous_response'] = "Sorry, I didn't get that. Would you like to play another round?"
        return question(session.attributes['previous_response'])
    session.attributes['game_state'] = False
    correct_lyric = session.attributes['correct_lyric']
    session.attributes['counter'] += 1

    if compare_lyric(lyric, correct_lyric):
        session.attributes['win_counter'] += 1
        response = '<speak> Correct.'
    else:
        response = '<speak> Incorrect. The lyrics were <break time ="500ms"/>' + correct_lyric +\
                   '. The song was ' + session.attributes['song'] + ' by ' + session.attributes['artist'] + '.'

    if not session.attributes['songs']:
        return end_game(response + '<break time="500ms"/> You\'ve completed the game. </speak>')

    session.attributes['previous_response'] = response + ' <break time="500ms"/> Would you like to play another round?</speak>'
    return question(session.attributes['previous_response'])


@ask.intent('RepeatIntent')
def repeat():
    return question(session.attributes['previous_response'])


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

