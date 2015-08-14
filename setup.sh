mkvirtualenv workshop --python=`which python3`
pip install -r requirements.txt
python -c "
from models import db, Group, Player, Puzzle, Answer
db.connect()
db.create_tables([Group, Player, Puzzle, Answer])
"
