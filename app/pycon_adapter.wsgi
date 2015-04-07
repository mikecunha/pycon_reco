import sys, os, bottle

sys.path = ['/path/to/apache/www/'] + sys.path
os.chdir(os.path.dirname(__file__))

os.environ[ 'MPLCONFIGDIR' ] = '/tmp/'

import pycon_service # This loads your application

application = bottle.default_app()