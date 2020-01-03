import time
import mysql.connector
import multiprocessing as mp

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

	yt = YouTube(url = url)
	title = yt.player_config_args["player_response"]["videoDetails"]["title"]
	duration = yt.player_config_args["player_response"]["videoDetails"]["lengthSeconds"]
	thumbnail_url = yt.player_config_args["player_response"]["videoDetails"]["thumbnail"]["thumbnails"][0]["url"].replace("hqdefault", "mqdefault").split("?")[0]

	if duration == 0:
		db_conn.commit()
		return

	db_curr = db_conn.cursor()

	ps = "INSERT INTO song_queue (url, status, title, thumbnail_url, duration) VALUES (%s, %s, %s, %s, %s)"

	db_curr.execute("USE music_player")
	db_curr.execute(ps, (url, 0, title, thumbnail_url, duration))

	db_conn.commit()
	db_curr.close()

app = Flask(__name__)

@app.route("/mp", methods = ["POST"])
def receive_req():
	req_json = None
	req_type = None
	try:
		req_json = request.get_json()
		req_type = req_json["type"]

		try:
			if (req_type == "new"):
				req_url = req_json["url"]
				send_new_song(req_url)
		except Exception as e:
			print("Error adding url: " + req_url)

	except Exception as e:
		print("Invalid request: " + str(request.get_data()))
		return "0"

	return "1"

def listener_thread():
	app.run(port = 5000)

def start_listener():
	p = mp.Process(target = listener_thread)
	p.start()