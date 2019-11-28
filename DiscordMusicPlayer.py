import asyncio
import concurrent.futures
import contextlib
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient

import getpass
import multiprocessing as mp
import mysql.connector
import os
from pytube import YouTube
import subprocess
import sys
import time
import threading
import wave

client = discord.Client()

class Attribs():
	db_pass = None
	vc = None
	skip_flag = mp.Value('d', 0)

def clean_yt_url(url):
	return url.split("&")[0]

def clean_files():
	try:
		os.system("rm -f \"tmp_song.wav\"")
	except Exception as e:
		print(e)

def is_video(filename):
	filename = filename.lower()
	filename = filename.replace("https://", "")
	filename = filename.replace("http://", "")
	filename = filename.replace("www.", "")
	return (filename.startswith("youtube.com") or filename.startswith("youtu.be"))

def get_current_url(hostname, username, password):
	db_conn = mysql.connector.connect(
		host = hostname,
		user = username,
		passwd = password
	)

	db_curr = db_conn.cursor()

	db_curr.execute("USE music_player")

	db_curr.execute("SELECT * FROM (SELECT * FROM song_queue WHERE status = 0) AS subq1 WHERE id = (SELECT min(id) FROM (SELECT * FROM song_queue WHERE status = 0) AS subq2)")

	url_row = None
	try:
		url_row = db_curr.fetchall()[0]
	except Exception as e:
		db_conn.commit()
		db_curr.close()
		return None

	url_row = (url_row[0], url_row[1])
	db_conn.commit()
	db_curr.close()
	return url_row

def set_done(hostname, username, password, row_id):
	db_conn = mysql.connector.connect(
		host = hostname,
		user = username,
		passwd = password
	)

	db_curr = db_conn.cursor()

	db_curr.execute("USE music_player")
	db_curr.execute("UPDATE song_queue SET status = 1 WHERE id = " + str(row_id))

	db_conn.commit()
	db_curr.close()

def add_song(hostname, username, password, url):
	db_conn = mysql.connector.connect(
		host = hostname,
		user = username,
		passwd = password
	)

	db_curr = db_conn.cursor()

	ps = "INSERT INTO song_queue (url, status) VALUES (%s, %s)"

	db_curr.execute("USE music_player")
	db_curr.execute(ps, (url, 0))

	db_conn.commit()
	db_curr.close()

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

def on_message_ind(message):
	try:
		if message.author == client.user:
			return

		author = message.author
		content = message.content

		channel = None
		if author.voice is not None:
			channel = author.voice.channel

		if content == "-bjoin" and channel is not None:
			while Attribs.vc and Attribs.vc.is_connected():
				try:
					latest_row = get_current_url("localhost", "host", Attribs.db_pass)
					if latest_row is not None:
						row_id = latest_row[0]
						url = latest_row[1]
						url = clean_yt_url(url)
						
						p = subprocess.Popen(["youtube-dl", "-q", "-x", "--no-part", "--abort-on-error", "--socket-timeout", "15", "--audio-format", "wav", "--output", "tmp_song.wav", url])
						p.wait(30)

						duration = 0
						with contextlib.closing(wave.open("tmp_song.wav", "r")) as f:
							frames = f.getnframes()
							rate = f.getframerate()
							duration = frames / float(rate)

						Attribs.vc.play(discord.FFmpegPCMAudio("tmp_song.wav"), after=lambda e: print('done', e))

						while Attribs.vc.is_connected() and Attribs.vc.is_playing() and Attribs.skip_flag.value == 0:
							time.sleep(1)

						Attribs.skip_flag.value = 0
						clean_files()
						set_done("localhost", "host", Attribs.db_pass, row_id)
						Attribs.vc.stop()
					else:
						time.sleep(1)
				except Exception as e:
					print(e)
					clean_files()
					set_done("localhost", "host", Attribs.db_pass, row_id)

		elif content.startswith("-badd"):
			url = content.split(" ")
			if len(url) > 1 and is_video(url[1]):
				add_song("localhost", "host", Attribs.db_pass, url[1])

		elif content == ("-bskip"):
			Attribs.skip_flag.value = 1

	except Exception as e:
		print(e)

@client.event
async def on_message(message):
	try:
		if message.author == client.user:
			return

		content = message.content
		author = message.author

		channel = None
		if author.voice is not None:
			channel = author.voice.channel

		if content == "-bjoin":
			Attribs.vc = await channel.connect()
			p = mp.Process(target = on_message_ind, args = (message,))
			p.start()
		elif content == "-bleave":
			server = message.guild.voice_client
			await server.disconnect()
			Attribs.vc = None
			clean_files()

		else:
			p = mp.Process(target = on_message_ind, args = (message,))
			p.start()

	except Exception as e:
		print(e)
	
def main():

	if len(sys.argv) != 2:
		print("Usage: $python3 DiscordMusicPlayer.py <token_file>")
		return

	token = None

	token_file = sys.argv[1]
	with open(token_file) as tf:
		token = tf.readline().strip()

	Attribs.db_pass = getpass.getpass()

	client.run(token)

if __name__ == "__main__":
	main()
