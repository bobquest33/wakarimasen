
SQL_POOLING = True
SQL_POOL_SIZE = 100
SQL_POOL_MAX_OVERFLOW = 10

SQL_ADMIN_TABLE = 'admin'
SQL_PROXY_TABLE = 'proxy'
SQL_REPORT_TABLE = 'reports'
SQL_BACKUP_TABLE = '__waka_backup'
SQL_ACCOUNT_TABLE = 'staff_accounts'
SQL_STAFFLOG_TABLE = 'staff_activity'
SQL_COMMON_SITE_TABLE = 'board_index'
SQL_PASSPROMPT_TABLE = 'passprompt'
SQL_PASSFAIL_TABLE = 'passfail'
USE_TEMPFILES = 1
DATE_STYLE = 'futaba'
ERRORLOG = ''
HOME = '/'
TIME_OFFSET = 0
JS_FILE = 'wakaba3.js'

CONVERT_COMMAND = ''
USE_TEMPFILES = 1

USE_SECURE_ADMIN = 0
USE_XHTML = 0
CHARSET = 'utf-8'
CONVERT_CHARSETS = 1
PAGE_EXT = '.html'
HTACCESS_PATH = './'
WAKABA_VERSION = ''
WAKARIMASEN_VERSION = '' # we should put something here
ALTERNATE_REDIRECT = 0

SPAM_FILES = ['spam.txt']

MAX_FCGI_LOOPS = 250

REPORT_COMMENT_MAX_LENGTH = 250
REPORT_RENZOKU = 60

REPORT_RETENTION = 60*24*3600
STAFF_LOG_RETENTION = 60*24*3600

PROXY_WHITE_AGE = 14*24*3600
PROXY_BLACK_AGE = 14*24*3600

POST_BACKUP = 1
POST_BACKUP_EXPIRE = 3600*24*14
PASSPROMPT_EXPIRE_TO_FAILURE = 300
PASSFAIL_THRESHOLD = 5
PASSFAIL_ROLLBACK = 1*24*3600
REPLIES_PER_STICKY = 1
ENABLE_ABBREVIATED_THREAD_PAGES = 0
POSTS_IN_ABBREVIATED_THREAD_PAGES = 50
ENABLE_RSS = 1
RSS_LENGTH = 10
RSS_WEBMASTER = ''

BOARD_DIR = ''
DEBUG = False
SERVER_NAME = 'localhost'
IDENTIFY_COMMAND = 'identify'
FG_ANIM_COLOR = 'white'
BG_ANIM_COLOR = '#660066'

ICONS = {}

HCAPTCHA = False
HCAPTCHA_QUESTION = 'desu'
HCAPTCHA_ANSWER = 'desu'
HCAPTCHA_COOKIE_BYPASS = True
HCAPTCHA_NOKOSAGE_BYPASS = True

NUKE_TIME_THRESHOLD = 30*24*3600

# add default values to config.py
import util as _util
_util.module_default('config', locals())
