import glob
import os
from db import open_conn, close_conn
import psycopg2 as pg

def parse_transcription_txt(subdir, filename, source_dir):
    subdir = subdir[len(source_dir):]
    transcripts = []
    speaker_id = os.path.split(filename)[-1].split('.')[0]

    with open(filename) as fp:
        line = fp.readline()
        while line:
            line = line.replace('\n', '').lower()
            if line[:len(speaker_id)] == speaker_id:
                audio_fname = line.split(' ')[0]
                dict = {}
                conn, cursor = open_conn()
                sql = "update voice_audio set transcription = '{}' where source_subdir = '{}' AND base_filename = '{}'".format(line[len(audio_fname) + 1:].replace("'", "''"), subdir, audio_fname)
                cursor.execute(sql)
                conn.commit()
                print(cursor.statusmessage)
                '''voice_id = cursor.fetchone()[0]
                close_conn(conn, cursor)
                dict['target_audio_id'] = voice_id
                dict['filepath'] = filename
                dict['source_type'] = 'target'
                dict['lang'] = 'eng'
                dict['content'] = line[len(audio_fname) + 1:]
                transcripts.append(dict)'''

            elif len(transcripts):
                transcripts[len(transcripts) - 1]['text'] += ' ' + line

            line = fp.readline()

    return transcripts


def insert_to_transcription_many(source_dir):
    fnames_in = sorted(list(glob.iglob(os.path.join(source_dir, '**'), recursive=False)))
    trans_list = []

    for fname in fnames_in:
        if os.path.isdir(fname):
            subdirs = [f.path for f in os.scandir(fname) if f.is_dir()]

            for subdir in subdirs:
                transcripts = sorted(list(glob.iglob(os.path.join(subdir, '**'), recursive=False)))

                for transcript in transcripts:
                    if transcript[-4:].lwero() == '.txt':
                        dict = parse_transcription_txt(subdir, transcript, source_dir)
                        for d in dict:
                            trans_list.append(d)
    print(trans_list)
    '''sql = "INSERT INTO voice_audio(target_audio_id, filepath, source_type, lang, content) VALUES(%(target_audio_id)s,\    conn, cursor = open_conn()

        %(filepath)s, %(source_type)s, %(lang)s, %(content)s)"
    print(cursor.statusmessage)    cursor.executemany(sql, trans_list)


    conn.commit()
    close_conn(conn, cursor)'''


def full_text_search(text):
    conn, cursor = open_conn()
    sql = "SELECT * FROM voice_audio WHERE make_tsvector(transcription) @@ to_tsquery('" + text + "\')"
    cursor.execute(sql)
    resp = cursor.fetchall()
    close_conn(conn, cursor)
    return resp


def get_top_n_words(n):
    conn, cursor = open_conn()
    sql = "SELECT * FROM ts_stat($$SELECT to_tsvector('english', transcription) FROM voice_audio) ORDER BY ndoc DESC " \
          "LIMIT {}".format(n)
    cursor.execute(sql)
    resp = cursor.fetchall()
    conn.commit()
    close_conn(conn, cursor)
    return resp


def select_random():
    conn, cursor = open_conn()
    sql = "SELECT base_filename, source_subdir, source_name FROM voice WHERE not exists (SELECT audio_id FROM" \
          " transcription WHERE audio_id = voice.id) ORDER BY random() LIMIT 1;"
    cursor.execute(sql)
    item = cursor.fetchone()
    sql = "SELECT base_filename, file_extension, source_subdir, source_dir FROM voice_and_source WHERE ( base_filename = " \
          + item[0] + " AND file_extension = " + item[1] + " AND source_name = " + item[3] + ");"
    cursor.execute(sql)
    file = cursor.fetchone()
    close_conn(conn, cursor)
    return os.path.join(file[3] + file[2], file[0] + '.' + file[1])


