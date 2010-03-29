import model
from template import Template
from util import WakaError

def no_task(environ, start_response):
    board = environ['waka.board']
    board.build_cache(environ)
    start_response('302 Found', [('Location', board.url)])
    return []

def init_database():
    model.metadata.create_all()
    # TODO: cleanup backups table

def error(environ, start_response, error):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return Template('error_template', error=error.message, environ=environ)
