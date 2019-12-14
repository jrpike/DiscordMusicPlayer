import multiprocessing as mp

class Attribs():
	db_hostname = "localhost"
	db_user = "host"
	db_pass = None
	vc = None
	skip_flag = mp.Value('d', 0)