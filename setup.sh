mkvirtualenv -p python3 puzzle-hunt
pip install -r requirements.txt
mkdir static
mkdir static/images
mkdir static/videos
python -c "
from models import db, Group, Player, Puzzle, Answer
db.connect()
db.create_tables([Group, Player, Puzzle, Answer])
"
