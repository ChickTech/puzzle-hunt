"""
Usage:

python tools/answer.py Icebreaker 1 "Who is the youngest?" Angela
"""

import sys
import requests

# print(sys.argv)
puzzle_name, player_id, question, answer = sys.argv[1:]

url = 'http://localhost:5000/answer/'

data = dict(
    puzzle=puzzle_name,
    player_id=player_id,
    question=question,
    answer=answer,
)
res = requests.post(url, data=data)
print(res.text)
