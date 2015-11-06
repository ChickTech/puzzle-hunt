"""
Usage:

python tools/register.py 1 "Bonzai Bill"
"""

import sys
import requests

group, player = sys.argv[1:]

url = 'http://localhost:5000/register/'

res = requests.post(url, data=dict(group=group, player=player))
print(res.text)
