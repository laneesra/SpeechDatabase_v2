import psycopg2 as pg
import time
from scipy.spatial import KDTree

def open_conn():
    conn = pg.connect(dbname='speech', user='postgres', password='080998', host='localhost')
    cursor = conn.cursor()

    return conn, cursor


def close_conn(conn, cursor):
    cursor.close()
    conn.close()


def get_top_n_words(10)
    with open('/home/laneesra/Рабочий стол/romeo_and_juliet.txt', 'r') as f:
		text = f.read()
		lines = text.split('\n')
		for line in lines:
		    line = line.replace('  ', '')
		    line = line.replace("'", '')
		    words = line.split(' ')
		    print(line)
		    for w in words:
		        if len(w):
		            conn, cursor = open_conn()
		            sql = "insert into text_search(text_field) values('{}');".format(w)
		            cursor.execute(sql)
		            conn.commit()

def test_speaker_recognition():
	conn, cursor = open_conn()
	array = [random.random() for i in range(100)]

	sql = "SELECT * FROM (" \
		"SELECT id, feature_vector, feature_vector <-> cube(array{}) "\
		"AS distance FROM speaker) AS x " \
		"ORDER BY distance ASC LIMIT 1;".format(array)
	start = time.time()
	cursor.execute(sql)
	resp = cursor.fetchall()
	conn.commit()
	close_conn(conn, cursor)
	print(time.time() - start)
	print(resp)
	import time

	conn, cursor = open_conn()
	start = time.time()

	sql = "SELECT id, feature_vector FROM speaker"
	cursor.execute(sql)
	resp = cursor.fetchall()
	features = []
	for r in resp:
		ar = r[1].replace('(', '').replace(')', '').split(', ')
		ar = [float(f) for f in ar]
		features.append(ar)
	tree = KDTree(features)
	start2 = time.time()
	print(tree.query(array, 1))
	print(time.time() - start2)
	print(time.time() - start)
