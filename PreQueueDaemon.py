import time
import mysql.connector
import multiprocessing as mp

from pytube import YouTube

def add_pq_row(hostname, username, password, url):
	db_conn = mysql.connector.connect(
		host = hostname,
		user = username,
		passwd = password
	)

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

def set_pq_row_done(hostname, username, password, row_id):
	db_conn = mysql.connector.connect(
		host = hostname,
		user = username,
		passwd = password
	)

	db_curr = db_conn.cursor()

	db_curr.execute("USE music_player")
	db_curr.execute("UPDATE pre_queue SET status = 1 WHERE id = " + str(row_id))

	db_conn.commit()
	db_curr.close()

def pq_daemon_thread(hostname, username, password):
	while True:
		db_conn = mysql.connector.connect(
			host = hostname,
			user = username,
			passwd = password
		)

		db_curr = db_conn.cursor()
		db_curr.execute("USE music_player")
		db_curr.execute("SELECT * FROM pre_queue WHERE status = 0")

		pre_rows = None
		try:
			pre_rows = db_curr.fetchall()
		except Exception as e:
			db_conn.commit()
			db_curr.close()
			return None

		ids = []
		for pre_row in pre_rows:
			ids.append(pre_row[0])
			url = pre_row[1]
			add_pq_row(hostname, username, password, url)

		db_conn.commit()
		db_curr.close()

		for id in ids:
			set_pq_row_done(hostname, username, password, id)

		time.sleep(0.5)

def start_pq_daemon(hostname, username, password):
	p = mp.Process(target = pq_daemon_thread, args = (hostname, username, password,))
	p.start()