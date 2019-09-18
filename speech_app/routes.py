import pathlib

from aiohttp import web

from .views import SiteHandler

PROJECT_PATH = pathlib.Path(__file__).parent


def init_routes(app: web.Application, handler: SiteHandler) -> None:
    add_route = app.router.add_route

    add_route('GET', '/', handler.index, name='index')
    add_route('GET', '/transcription', handler.transcription, name='transcription')
    add_route('GET', '/speaker_recognition', handler.speaker_recognition, name='speaker_recognition')
    add_route('GET', '/test_transcription', handler.test_transcription, name='test_transcription')
    add_route('GET', '/get_audio_for_marking', handler.get_audio_for_marking, name='get_audio_for_marking')
    add_route('POST', '/ident_speaker', handler.ident_speaker, name='ident_speaker')
    add_route('POST', '/mark_transcript', handler.mark_transcript, name='mark_transcript')
    add_route('POST', '/recognize_speech', handler.recognize_speech, name='recognize_speech')
    add_route('GET', '/adding', handler.adding, name='adding')
    add_route('GET', '/mark_data', handler.mark_data, name='mark_data')
    add_route('POST', '/keyword_search', handler.keyword_search, name='keyword_search')
    add_route('POST', '/get_top', handler.get_top, name='get_top')
    add_route('POST', '/add_transcript', handler.add_transcript, name='add_transcript')



    # added static dir
    app.router.add_static(
        '/static/', path=(PROJECT_PATH / 'static'), name='static'
    )

