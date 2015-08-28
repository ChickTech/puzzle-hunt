import io
import random
import os.path as op
from flask import Flask, request, render_template, url_for
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView
import pyqrcode
from geopy.distance import vincenty
import peewee

from models import db, Group, Player, Puzzle, Answer

HERE = op.abspath(op.dirname(__file__))
STATIC_DIR = op.join(HERE, 'static')
MAX_CONTENT_LENGTH = 1024 * 1024


app = Flask(__name__)
admin = Admin(app, name='Puzzle Hunt', template_mode='bootstrap3')
admin.add_view(ModelView(Group))
admin.add_view(ModelView(Player))
admin.add_view(ModelView(Puzzle))
admin.add_view(ModelView(Answer))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register/<group_name>/<player_name>')
def register(group_name, player_name):
    group_name = group_name.strip()
    player_name = player_name.strip()

    group, _ = Group.get_or_create(name=group_name)

    try:
        player = Player.get(group=group, name=player_name)
    except Player.DoesNotExist:
        player = Player.create(
            group=group, name=player_name, order=group.players.count())

    return str(player.id)


@app.route('/groups')
def groups():
    return render_template('groups.html', groups=Group.select())


@app.route('/groups/<group_name>')
def group(group_name):
    group_answers = []
    for puzzle in Puzzle.select().order_by(Puzzle.name):
        puzzle_answers = (
            puzzle.answers.select()
            .join(Player).join(Group)
            .where(Group.name == group_name)
        )
        group_answers.append((puzzle.name, puzzle_answers))

    return render_template(
        'group.html',
        group=Group.get(Group.name == group_name),
        group_answers=group_answers)


@app.route('/distance/<coords>')
def distance(coords):
    # Convert coordinates from string to float.
    lat1, long1, lat2, long2 = [float(s) for s in coords.split(',')]
    # Return the distance in miles.
    result = vincenty((lat1, long1), (lat2, long2)).miles
    # Convert back to string.
    return str(result)


@app.route('/qrcode/<text>')
def qrcode(text):
    buffer = io.BytesIO()
    code = pyqrcode.create(text)
    code.svg(buffer, scale=8, background='white')
    return buffer.getvalue()


@app.route('/answer/<puzzle_name>/<player_id>/<question>', methods=['POST'])
def answer(puzzle_name, player_id, question):
    set_answer(puzzle_name, player_id, question, 'text', request.get_data())
    return 'Answer submitted'


@app.route('/upload-image/<puzzle_name>/<player_id>/<question>', methods=['POST'])
def upload_image(puzzle_name, player_id, question):
    if request.content_length > MAX_CONTENT_LENGTH:
        return 'Images cannot be larger than 1 MB'
    set_answer(puzzle_name, player_id, question, 'image', request.get_data())
    return 'Image submitted'


@app.route('/upload-video/<puzzle_name>/<player_id>/<question>', methods=['POST'])
def upload_video(puzzle_name, player_id, question):
    if request.content_length > MAX_CONTENT_LENGTH:
        return 'Videos cannot be larger than 1 MB'
    set_answer(puzzle_name, player_id, question, 'video', request.get_data())
    return 'Video submitted'


ICEBREAKER_QUESTIONS = [
    'Who has the longest full name?',
    'Who is the youngest?',
    'Who traveled the farthest to be here?',
    'Who has the most siblings?',
    'Who keeps the most pets?',
]

@app.route('/icebreaker/<player_id>')
def icebreaker(player_id):
    player = Player.get(Player.id == player_id)
    return ICEBREAKER_QUESTIONS[player.order]


DOODLE_ASSIGNMENTS = [
    'cat whiskers',
    'bunny ears',
    'crabby hands',
    'a frog tongue catching a fly',
    'viking helment',
]

@app.route('/doodle/<player_id>')
def doodle(player_id):
    player = Player.get(Player.id == player_id)
    return DOODLE_ASSIGNMENTS[player.order]


SIGN_LANGUAGE_ASSIGNMENTS = [
    'hamburger',
    'sleep',
    'angry',
    'who',
    'bird',
]

@app.route('/sign-language/<player_id>')
def sign_language(player_id):
    player = Player.get(Player.id == player_id)
    return SIGN_LANGUAGE_ASSIGNMENTS[player.order]


WHO_AM_I_CLUES = [
    ('POTOMAC', 'a famous river'),
    ('QUINCY', 'a brown line stop'),
    ('DIPPING', 'a hummus-related action'),
    ('INTERVIEW', 'a type of conversation'),
]

@app.route('/who-am-i/<player_id>')
def who_am_i(player_id):
    player = Player.get(Player.id == player_id)
    anagram, description = WHO_AM_I_CLUES[player.order]
    # Shuffle the letters.
    anagram = list(anagram)
    random.shuffle(anagram)
    anagram = ''.join(anagram)
    return '%s|%s' % (anagram, description)


def set_answer(puzzle_name, player_id, question, content_type, content):
    player = Player.get(Player.id == player_id)
    puzzle, _ = Puzzle.get_or_create(name=puzzle_name)
    try:
        answer = Answer.get(
            (Answer.puzzle == puzzle) & (Answer.player == player))
    except Answer.DoesNotExist:
        answer = Answer(puzzle=puzzle, player=player)

    answer.question = question

    if content_type == 'text':
        answer.value = content
    elif content_type == 'image':
        filename = '%s_%s.jpg' %  (puzzle.id, player.id)
        path = '%s/images/%s' % (STATIC_DIR, filename)
        with open(path, 'wb') as fp:
            fp.write(content)
        answer.value = 'image:' + filename
    elif content_type == 'video':
        filename = '%s_%s.mp4' %  (puzzle.id, player.id)
        path = '%s/videos/%s' % (STATIC_DIR, filename)
        with open(path, 'wb') as fp:
            fp.write(content)
        answer.value = 'video:' + filename

    answer.save()


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(host='0.0.0.0', debug=True)
