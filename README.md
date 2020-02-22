# DiscordMusicPlayer

Install web dependencies:<br />
`$ sudo apt-get install mysql-server`<br />
`$ sudo apt-get install ffmpeg`<br />
`$ sudo apt-get install apache2`<br />
`$ sudo apt-get install php libapache2-mod-php php-mysql`<br />

Prioritize index.php in apache2 conf:<br />
`$ sudo nano /etc/apache2/mods-enabled/dir.conf`<br />
`$ sudo systemctl restart apache2`<br />

Install youtube-dl:<br />
`$ sudo wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl`<br />
`$ sudo chmod a+rx /usr/local/bin/youtube-dl`<br />

Install Python libraries:<br />
`$ sudo pip3 install mysql-connector`<br />
`$ sudo pip3 install mysql-connector-python`<br />
`$ sudo pip3 install pytube`<br />

Setup database:<br />
`$ sudo mysql -u root`<br />
`> SOURCE setup.sql`<br />
