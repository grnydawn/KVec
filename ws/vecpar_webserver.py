import os, os.path
import sys
import random
import sqlite3
import string
import time

import cherrypy
import Pyro4

script_dir = os.path.dirname(os.path.realpath(__file__))
backend_dir = '%s/../vb'%script_dir
sys.path.append(backend_dir)


DB_STRING = "my.db"
TAB = 4

sys.excepthook = Pyro4.util.excepthook

backend = None
req_filename = None
req_srclines = None

cherrypy.config.update( { \
    'log.access_file': '%s/access.log'%script_dir, \
    'log.error_file': '%s/error.log'%script_dir, \
    'server.socket_port': 8080 \
})

def strtohtml(line):
    #dstr = line.decode('utf-8')
    ostr = ''
    for c in line:
        if c==' ':  ostr += '&nbsp;'
        elif c=='\t': ostr += '&nbsp;'*TAB
        elif c=='\n': ostr += '<br>\n'
        else: ostr += c
    return ostr
    #return ostr.encode('utf-8')

class KVecPortal(object):
   @cherrypy.expose
   def index(self):
       return open('%s/index.html'%script_dir)

class UploaderWebService(object):
    exposed = True

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
#        with sqlite3.connect(DB_STRING) as c:
#            cherrypy.session['ts'] = time.time()
#            r = c.execute("SELECT value FROM user_string WHERE session_id=?",
#                [cherrypy.session.id])
#            return r.fetchone()
        pass

    #def POST(self, length=8):
    def POST(self, **kwargs):
        global req_filename, req_srclines

        #import pdb; pdb.set_trace()
        for key, value in kwargs.iteritems():
            if key=='prog_file':
                s = ''
                if isinstance(value, list):
                    for part in value:
                        s += 'Content-Type: %s<br>'%part.headers['Content-Type']
                        _,_,filename = part.headers['Content-Disposition'].split(';')
                        s += 'filename: %s<br>'%filename.split('=')[1]
                        for line in part.file.readlines():
                            s += strtohtml(line)
                        s += '<br>\n'
                else:
                    if value.file is None:
                        s = 'No file is uploaded.<br>\n'
                    else:
                        content_type = value.headers['Content-Type']
                        _,_,filename = value.headers['Content-Disposition'].split(';')
                        if content_type==u'text/x-fortran':
                            req_filename = filename
                            req_srclines = value.file.readlines()

                        s += 'Content-Type: %s<br>'%content_type
                        _,_,filename = value.headers['Content-Disposition'].split(';')
                        s += 'filename: %s<br>'%filename.split('=')[1]
                        s += strtohtml(req_srclines)
                    s += '<br>\n'

                return s
#        length = 8
#        some_string = ''.join(random.sample(string.hexdigits, int(length)))
#        with sqlite3.connect(DB_STRING) as c:
#            cherrypy.session['ts'] = time.time()
#            c.execute("INSERT INTO user_string VALUES (?, ?)",
#                [cherrypy.session.id, some_string])
#        return some_string

    def PUT(self, another_string):
#        with sqlite3.connect(DB_STRING) as c:
#            cherrypy.session['ts'] = time.time()
#            c.execute("UPDATE user_string SET value=? WHERE session_id=?",
#                [another_string, cherrypy.session.id])
        pass

    def DELETE(self):
#        cherrypy.session.pop('ts', None)
#        with sqlite3.connect(DB_STRING) as c:
#            c.execute("DELETE FROM user_string WHERE session_id=?",
#                [cherrypy.session.id])
        pass

class BuilderWebService(object):

    @cherrypy.expose
    def index(self, **kwargs):

        ret_str = 'Unknown command: %s'%str(kwargs)
        if 'build' in kwargs:
            if req_srclines:
                backend.create_order('build', req_filename, req_srclines, kwargs['build'])
                ret_str = backend.get_order_status('build')
        elif 'getinfo' in kwargs:
            req = kwargs['getinfo']
            if req=='ref_result':
                ret_str = backend.get_order_status('build')

        #import pdb; pdb.set_trace()
        return ret_str


def setup_database():
    """
    Create the `user_string` table in the database
    on server startup
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("CREATE TABLE user_string (session_id, value)")

def cleanup_database():
    """
    Destroy the `user_string` table from the database
    on server shutdown.
    """
    with sqlite3.connect(DB_STRING) as con:
        con.execute("DROP TABLE user_string")

def start():
    global backend

    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': script_dir
        },
        '/upload': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/execute': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

    cherrypy.engine.subscribe('start', setup_database)
    cherrypy.engine.subscribe('stop', cleanup_database)

    webapp = KVecPortal()
    webapp.upload = UploaderWebService()
    webapp.execute = BuilderWebService()

    cherrypy.tree.mount(webapp, '/', conf)

    ns = Pyro4.locateNS()
    backend = Pyro4.Proxy("PYRONAME:kvec.backend")

    cherrypy.engine.start()
    cherrypy.engine.block()
    #cherrypy.quickstart(webapp, '/', conf)

def stop():
    cherrypy.engine.exit()

if __name__ == '__main__':
    start()
