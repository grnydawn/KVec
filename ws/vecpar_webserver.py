import random
import string

import cherrypy

class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return """<html>
          <head></head>
          <body>
            <form method="post" action="generate">
              <input type="text" value="8" name="length" />
              <button type="submit">Give it now!</button>
            </form>
          </body>
        </html>"""

    @cherrypy.expose
    def generate(self, length=8):
        return ''.join(random.sample(string.hexdigits, int(length)))

def start():
    cherrypy.quickstart(StringGenerator())

def stop():
    cherrypy.engine.exit()

if __name__ == '__main__':
    cherrypy.quickstart(StringGenerator())
