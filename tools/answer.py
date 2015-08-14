"""
Usage:

python tools/answer.py Icebreaker 1 "Who is the youngest?" Angela
"""

import sys
import requests

# print(sys.argv)
puzzle_name, player_id, question, value = sys.argv[1:]

url = 'http://localhost:5000/answer/%s/%s/%s' % (
    puzzle_name, player_id, question)

res = requests.post(url, data=value)
print(res.text)
