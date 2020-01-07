import codecs
import time
import json
import mysql.connector
import multiprocessing as mp
import sys

from Attributes import Attribs
from flask import Flask, request, jsonify
from pytube import YouTube

def is_video(filename):
	if filename is None:
		return False

	filename = filename.lower()
	filename = filename.replace("https://", "")
	filename = filename.replace("http://", "")
	filename = filename.replace("www.", "")
	return (filename.startswith("youtube.com") or filename.startswith("youtu.be"))

def send_new_song(url):
	db_conn = mysql.connector.connect(
		host = Attribs.db_hostname,
		user = Attribs.db_user,
		passwd = Attribs.db_pass
	)

	if not is_video(url):
		return

	title = "Generic"
	duration = 1
	thumbnail_url = "https://cdn.dribbble.com/users/93362/screenshots/3647605/youtube-music-icon.jpg"
	try:
		yt = YouTube(url = url)
		title = yt.player_config_args["player_response"]["videoDetails"]["title"]
		duration = yt.player_config_args["player_response"]["videoDetails"]["lengthSeconds"]
		thumbnail_url = yt.player_config_args["player_response"]["videoDetails"]["thumbnail"]["thumbnails"][0]["url"].replace("hqdefault", "mqdefault").split("?")[0]
	except Exception as e:
		pass

	if duration == 0:
		db_conn.commit()
		return

	db_curr = db_conn.cursor()

	ps = "INSERT INTO song_queue (url, status, title, thumbnail_url, duration) VALUES (%s, %s, %s, %s, %s)"

	db_curr.execute("USE music_player")
	db_curr.execute(ps, (url, 0, title, thumbnail_url, duration))

	db_conn.commit()
	db_curr.close()

def delete_song(id_to_delete):
	db_conn = mysql.connector.connect(
		host = Attribs.db_hostname,
		user = Attribs.db_user,
		passwd = Attribs.db_pass
	)

	db_curr = db_conn.cursor()

	ps = "SELECT id FROM song_queue WHERE status = 0"

	db_curr.execute("USE music_player")
	db_curr.execute(ps)

	id_row = None
	try:
		tmp_id = 0
		for id_row in db_curr.fetchall():
			id_row = id_row[0]

			if tmp_id == id_to_delete - 1:
				break
			tmp_id += 1

	except Exception as e:
		db_conn.commit()
		db_curr.close()
		return None

	ps = "UPDATE song_queue SET status = 1 WHERE id = %s"
	db_curr.execute(ps, (id_row,))

	db_conn.commit()
	db_curr.close()

app = Flask(__name__)

@app.route("/postmethod", methods = ["POST"])
def receive_req():

	req_json = None
	req_type = None
	try:
		req_json = json.loads(request.get_data())
		req_type = req_json["type"]

		try:
			if (req_type == "new"):
				req_url = codecs.decode(req_json["url"], "unicode_escape")
				send_new_song(req_url)

			elif (req_type == "delete"):
				id_to_delete = int(req_json["id"])
				delete_song(id_to_delete)

		except Exception as e:
			print("Error adding url: " + str(req_json))
			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))

	except Exception as e:
		print("Invalid request: " + str(request.get_data()))
		print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(e)
		return "0"

	return "1"

def listener_thread():
	app.run(host = '0.0.0.0', port = 5000)

def start_listener():
	p = mp.Process(target = listener_thread)
	p.start()