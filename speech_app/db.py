import psycopg2 as pg

def init_db(conf):
    conn = pg.connect(
        database=conf.database,
        user=conf.user,
        password=conf.password,
        host=conf.host,
        port=conf.port,
    )
    cursor = conn.cursor()
    return {'cursor': cursor, 'conn': conn}


def open_conn():
    conn = pg.connect(dbname='speech', user='postgres', password='080998', host='localhost')
    cursor = conn.cursor()

    return conn, cursor


def close_conn(conn, cursor):
    cursor.close()
    conn.close()


def get_nearest(features_str):
    conn, cursor = open_conn()
    sql = "SELECT * FROM (" \
        "SELECT id, feature_vector, feature_vector <-> cube({}) AS distance" \
        "FROM speaker) AS x ORDER BY distance ASC LIMIT 1;"
    cursor.execute(sql.format(features_str))
    resp = cursor.fetchone()
    conn.commit()
    close_conn(conn, cursor)
    return resp

def select_speaker_features(db):
    with db['conn'].cursor() as cursor:
        result = cursor.execute('SELECT id, feature_vector FROM speaker_id ORDER BY id')
        features = cursor.fetchall()
        print(cursor.statusmessage)
        return features



