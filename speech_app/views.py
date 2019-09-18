import asyncio
from typing import Dict
from concurrent.futures import ProcessPoolExecutor

import aiohttp_jinja2
from aiohttp import web

from .worker import recognize, ident_speaker, select_random_audio, keyword_search, get_top, add_transcript
from .utils import Config


class SiteHandler:
    def __init__(self, conf: Config, executor: ProcessPoolExecutor) -> None:
        self._conf = conf
        self._executor = executor
        self._loop = asyncio.get_event_loop()

    @aiohttp_jinja2.template('index.html')
    async def index(self, request: web.Request) -> Dict[str, str]:
        return {}

    @aiohttp_jinja2.template('transcription.html')
    async def transcription(self, request: web.Request) -> Dict[str, str]:
        return {}

    @aiohttp_jinja2.template('speaker_recognition.html')
    async def speaker_recognition(self, request: web.Request) -> Dict[str, str]:
        return {}

    @aiohttp_jinja2.template('adding.html')
    async def adding(self, request: web.Request) -> Dict[str, str]:
        return {}

    @aiohttp_jinja2.template('test_transcription.html')
    async def test_transcription(self, request: web.Request) -> Dict[str, str]:
        return {}

    @aiohttp_jinja2.template('mark_data.html')
    async def mark_data(self, request: web.Request) -> Dict[str, str]:
        return {}

    async def mark_transcript(self, request: web.Request) -> web.Response:
        return

    async def get_top(self, request: web.Request) -> web.Response:
        form = await request.post()
        raw_data = form['n']
        executor = request.app['executor']
        r = self._loop.run_in_executor
        raw_data = await r(executor, get_top, raw_data)
        headers = {'Content-Type': 'application/json'}
        return web.Response(body=raw_data, headers=headers)

    async def keyword_search(self, request: web.Request) -> web.Response:
        form = await request.post()
        raw_data = form['keyword']
        dataset = form['dataset']
        executor = request.app['executor']
        r = self._loop.run_in_executor
        raw_data = await r(executor, keyword_search, raw_data, dataset)
        headers = {'Content-Type': 'application/json'}
        return web.Response(body=raw_data, headers=headers)

    async def add_transcript(self, request: web.Request) -> web.Response:
        form = await request.post()
        raw_data = form['trans']
        id = form['id']
        print('here')
        executor = request.app['executor']
        r = self._loop.run_in_executor
        raw_data = await r(executor, add_transcript, raw_data, id)
        headers = {'Content-Type': 'application/json'}
        return web.Response(body=raw_data, headers=headers)

    async def get_audio_for_marking(self, request: web.Request) -> web.Response:
        executor = request.app['executor']
        r = self._loop.run_in_executor
        raw_data = await r(executor, select_random_audio)
        # raw_data = predict(raw_data)
        headers = {'Content-Type': 'application/json'}
        return web.Response(body=raw_data, headers=headers)

    async def recognize_speech(self, request: web.Request) -> web.Response:
        form = await request.post()
        raw_data = form['audio_data'].file.read()
        filename = form['filename']
        executor = request.app['executor']
        r = self._loop.run_in_executor
        raw_data = await r(executor, recognize, raw_data, filename)
        # raw_data = predict(raw_data)
        headers = {'Content-Type': 'application/json'}
        return web.Response(body=raw_data, headers=headers)

    async def ident_speaker(self, request: web.Request) -> web.Response:
        form = await request.post()
        raw_data = form['audio_data'].file.read()
        filename = form['filename']
        executor = request.app['executor']
        r = self._loop.run_in_executor
        raw_data = await r(executor, ident_speaker, raw_data, filename)
        # raw_data = predict(raw_data)
        headers = {'Content-Type': 'application/json'}
        return web.Response(body=raw_data, headers=headers)