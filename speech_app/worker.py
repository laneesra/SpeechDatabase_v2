import io
import json
import signal
import numpy as np
from typing import Tuple, Dict, Any, Optional
import speech_recognition as sr
from datetime import datetime
#import cv2 as cv
import time
import os
from pydub import AudioSegment
from .speaker_recognition import SpeakerRecognition
from .db import open_conn, close_conn

_model = None
OUTPUT = '/home/laneesra/PycharmProjects/speech_db/speech_app/imagetagger/data'

def warm(model_path: str, conf_db) -> None:
    # should be executed only in child processes
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    global _model
    if _model is None:
        _model = 'model'
        #_model = SpeakerRecognition(model_path, conf_db, OUTPUT)


def clean() -> None:
    # should be executed only in child processes
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    global _model
    _model = None


def keyword_search(raw_data: bytes, dataset: bytes) -> bytes:
    data: Dict[str, Any] = {}
    conn, cursor = open_conn()
    sql = "SELECT id, transcription FROM voice_audio WHERE make_tsvector(transcription) @@ to_tsquery('" + raw_data + "\') AND source_name = '{}'"
    cursor.execute(sql.format(dataset))
    resp = cursor.fetchall()
    close_conn(conn, cursor)
    data['response'] = [{'id': id, 'text': transcription}
                           for id, transcription in resp]

    data['success'] = True
    return json.dumps(data).encode('utf-8')

def add_transcript(raw_data: bytes, id: bytes) -> bytes:
    data: Dict[str, Any] = {}
    data['success'] = True
    return json.dumps(data).encode('utf-8')


def get_top(raw_data: bytes) -> bytes:
    data: Dict[str, Any] = {}
    conn, cursor = open_conn()
    sql = "SELECT word, ndoc, nentry FROM ts_stat($$SELECT to_tsvector('english', transcription) FROM voice_audio$$) ORDER BY nentry DESC " \
          "LIMIT {}".format(raw_data)
    cursor.execute(sql)
    resp = cursor.fetchall()
    conn.commit()
    close_conn(conn, cursor)
    print(resp)
    data['response'] = [{'keyword': word, 'n_entry': nentry}
                           for word, ndoc, nentry in resp]

    data['success'] = True
    return json.dumps(data).encode('utf-8')

def select_random_audio() -> bytes:
    data: Dict[str, Any] = {}
    conn, cursor = open_conn()
    sql = "SELECT base_filename, source_subdir, source_name, id  FROM voice_audio WHERE  transcription is null" \
          " ORDER BY random() LIMIT 1;"
    cursor.execute(sql)
    item = cursor.fetchone()
    print(item)
    sql = "SELECT base_filename, file_extension, source_subdir, source_dir FROM voice_and_source WHERE ( base_filename = '{}'" \
          " AND source_subdir = '{}' AND source_name = '{}');".format(item[0], item[1], item[2])
    cursor.execute(sql)
    file = cursor.fetchone()
    close_conn(conn, cursor)

    data['id'] = item[3]
    data['audio'] = os.path.join(file[3] + file[2], file[0] + '.' + file[1])
    data['success'] = True
    return json.dumps(data).encode('utf-8')

def ident_speaker(raw_data: bytes, filename, model: Optional[Any]=None) -> bytes:
    if model is None:
        model = _model

    if model is None:
        raise RuntimeError('Model should be loaded first')

    data: Dict[str, Any] = {}
    start = time.time()
    id, feature_vector = model.detect_voice(raw_data, filename)
    t = time.time() - start
    data['prediction'] = id
    data['time'] = '{:10.4f}s'.format(t)
    data['success'] = True
    return json.dumps(data).encode('utf-8')


def recognize(raw_data: bytes, filename) -> bytes:
    data: Dict[str, Any] = {}
    start = time.time()
    wav = io.BytesIO(raw_data)
    wav = AudioSegment.from_raw(wav, channels=1, frame_rate=44100, sample_width=2)
    if filename.split('.')[-1] not in ['wav']:
        filename += '.wav'
    data['filename'] = filename
    filename = os.path.join(OUTPUT, filename)
    wav.export(filename, format='wav')
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = r.record(source)
    t = time.time() - start
    print('time spent: ', t)
    #todo add to executer
    try:
        text = r.recognize_google(audio)
        print('text:', text)
    except sr.UnknownValueError:
        text = "Google Speech Recognition не может распознать речь на аудиозаписи"
    except sr.RequestError as e:
        text = "Невозможно получить ответ от сервиса Google Speech Recognition; {0}".format(e)
    data['prediction'] = text
    data['time'] = '{:10.4f}s'.format(t)
    data['success'] = True
    return json.dumps(data).encode('utf-8')
