"""
Usage:

python tools/upload_file.py Doodle 1 "Draw a mustache" ~/Downloads/image.jpg
python tools/upload_file.py "Sign Language" 1 "Bird" ~/Downloads/video.mp4
"""
import sys
import os.path as op
import requests

puzzle_name, player_id, question, path = sys.argv[1:]

ext = path.rsplit('.')[1]
if ext == 'jpg':
    command = 'upload-image'
else:
    command = 'upload-video'

url = 'http://localhost:5000/%s/%s/%s/%s' % (
    command, puzzle_name, player_id, question)

print(url)
res = requests.post(url, data=open(path, 'rb').read())
print(res.text)
