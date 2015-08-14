import io
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
    group, _ = Group.get_or_create(name=group_name)
    
    try:
        player = Player.get(group=group, name=player_name)
    except Player.DoesNotExist:
        player = Player.create(group=group, name=player_name, 
            order=group.players.count())
    
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
    return 'OK'


@app.route('/upload-image/<puzzle_name>/<player_id>/<question>', methods=['POST'])
def upload_image(puzzle_name, player_id, question):
    if request.content_length > MAX_CONTENT_LENGTH:
        return 'Images cannot be larger than 1 MB'
    set_answer(puzzle_name, player_id, question, 'image', request.get_data())
    return 'OK'


@app.route('/upload-video/<puzzle_name>/<player_id>/<question>', methods=['POST'])
def upload_video(puzzle_name, player_id, question):
    if request.content_length > MAX_CONTENT_LENGTH:
        return 'Videos cannot be larger than 1 MB'
    set_answer(puzzle_name, player_id, question, 'video', request.get_data())
    return 'OK'


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


# class SignLanguageView(FlaskView):
#     items = [
#         'Hamburger',
#         'Sleep',
#         'Angry',
#         'Who',
#         'Bird',
#     ]

#     @route('/assignment/<key>')
#     def item(self, key):
#         player = get_player(key)
#         return self.items[player.number]

#     @route('/answer/<key>/<value>')
#     def question(self, key, value):
#         set_answer('Sign Language', key, value)
#         return 'OK'

# SignLanguageView.register(app)


# class DoodleView(FlaskView):
#     assignments = [
#         'Elf ears',
#         'Cat whiskers',
#         'Bunny ears',
#         'Crabby hands',
#         'Viking helment',
#     ]

#     @route('/question/<key>')
#     def assignment(self, key):
#         player = get_player(key)
#         return self.assignments[player.number]

#     @route('/answer/<key>/<value>')
#     def question(self, key, value):
#         set_answer('Doodle', key, value)
#         return 'OK'

# DoodleView.register(app)


# class HistoryView(FlaskView):
#     items = [
#         ('POTOMAC', 'a famous river'),
#         ('QUINCY', 'a famous river'),
#         ('DIPPING', 'a famous river'),
#         ('INTERVIEW', 'a famous river'),
#     ]

#     @route('/clue/<key>')
#     def item(self, key):
#         player = get_player(key)
#         return self.items[player.number]

#     @route('/answer/<key>/<value>')
#     def question(self, key, value):
#         set_answer('History', key, self.items[player.number], value)
#         return 'OK'

# HistoryView.register(app)

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
