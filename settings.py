'''

Imports

'''


from decouple import config 
from pathlib import Path


'''

Constants

'''


BASE_DIR = Path(__file__).parent
COG_DIR = 'Cogs'
LOG_DIR = 'Logs'
DATA_DIR = 'Data'

PREFIXES = ['//']
MAX_PREFIXES = 5

TOKEN = config('TOKEN', default = None)
INVITE = config('INVITE', cast = str, default = 'http://google.com/')

