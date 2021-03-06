# Django settings for solarpermit project.
import os.path
import logging
import sys
reload(sys) # reload sys to force utf-8
sys.setdefaultencoding('utf-8') # forces utf-8 encoded strings
import site

DEBUG = False
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1',)
#SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

SOLARPERMIT_VERSION = '1.3.50'
SAMPLE_JURISDICTIONS=[1, 101105]

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS
#ADMIN_EMAIL_ADDRESS = 'kvo@aerio.com'
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
"""

#outgoing mail server settings
SERVER_EMAIL = ''
DEFAULT_FROM_EMAIL = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = ''
EMAIL_HOST=''
EMAIL_PORT=''
EMAIL_USE_TLS=False
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'
#TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

PROJECT_ROOT = os.path.dirname(__file__)
LOG_ROOT = os.path.join(PROJECT_ROOT, 'log')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

FIXTURE_DIRS = ( 
                os.path.join(os.path.dirname(__file__), 'website/fixture'),
                 )

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'compressor.finders.CompressorFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'zj8k!s68ar4m#zqk7o%)!e+^(cfme2%^86u#jb5&f&$-!qui=1'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django_jinja.loaders.AppLoader',
)
TEMPLATE_DIRS = (
    # because we're not using the FileSystemLoader to find templates,
    # we wouldn't really need this to be set except that
    # django-compressor requries it.
    os.path.join(os.path.dirname(__file__), 'website', 'templates')
)

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.StatsdMiddleware',               # must be first
    'django.middleware.common.CommonMiddleware',
    'tracking.middleware.VisitorTrackingMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'pre_django_authentication.ProcessPasswordMiddleWare',     
    #'require_login_middleware.RequireLoginMiddleware',     
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    'user_page_view.UserPageViewMiddleWare',     
    #'set_user_org_in_session.SetUserOrgInSessionMiddleWare',
    'django_statsd.middleware.StatsdMiddlewareTimer',          # must be last
)


LOGIN_URL = '/sign_in'


ROOT_URLCONF = 'urls'

FILE_UPLOAD_TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tmp').replace('\\','/')

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
)

ALLOWED_UPLOAD_FILE_TYPES = ('.jpg', '.jpeg', '.gif', '.bmp', '.png', '.tiff', '.txt', '.doc', '.pdf', '.zip', '.html', 'xlsx', '.docx', '.mp3', '.wmv', '.mp4')
MAX_UPLOAD_FILE_SIZE = 5 * 1024 * 1024 #result in bytes
ALLOWED_IMAGE_FILE_TYPES = ('.jpg', '.gif', '.png')
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    #'django.core.context_processors.i18n',
    'django.core.context_processors.auth', #this is required for admin
    #'django.core.context_processors.csrf', #necessary for csrf protection
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'south',
    'robots',
    'django_countries',
    'djcelery',
    'djkombu',
    'followit',  
    'sorl.thumbnail',
    'dajax',
    'localflavor',
    'website',
    'compressor',
    'tracking',
    'django_jinja',
    'autocomplete_light',
    'django_statsd',
    'impostor',
)

#setup memcached for production use!
#see http://docs.djangoproject.com/en/1.1/topics/cache/ for details
CACHE_BACKEND = 'locmem://'
#If you use memcache you may want to uncomment the following line to enable memcached based sessions
#SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'impostor.backend.AuthBackend',
)

#Celery Settings
BROKER_TRANSPORT = "djkombu.transport.DatabaseTransport"
CELERY_ALWAYS_EAGER = True

import djcelery
djcelery.setup_loader()
DOMAIN_NAME = 'localhost'

CSRF_COOKIE_NAME = 'solarpermit_csrf'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
    },
    'handlers': {
        'console': {
            'filters': ['require_debug_true'],
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
#        '': {
#            'handlers': ['console'],
#            'level': 'DEBUG',
#            'propagate': False, # this tells logger to send logging message
#                                # to its parent (will send if set to True)
#        },
        #'django.db': {
        #},
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

RECAPTCHA_USE_SSL = True

MAX_REC_PER_PAGE = 25

#SORT_DESC_IMG ='/m/solarpermit/media/images/sort-descending-icon.png'
#SORT_ASC_IMG = '/m/solarpermit/media/images/sort-ascending-icon.png'
SORT_DESC_IMG ='/media/images/sort-descending-black-icon.png'
SORT_ASC_IMG = '/media/images/sort-ascending-black-icon.png'
SORT_CLASS = 'sort'

DEFAULT_CONTENT_TYPE = 'text/html'

SITE_URL = "http://solarpermit.org/"
FIRST_MAX_FAILED_LOGIN_ATTEMPTS = 5
SECOND_MAX_FAILED_LOGIN_ATTEMPTS = 8
TIME_PERIOD_FOR_FAILED_LOGIN_ATTEMPTS = 5

#from jinja.contrib import djangosupport
#djangosupport.configure()

AUTH_PROFILE_MODULE = 'website.UserDetail'

GOOGLE_API_KEY = '' # needed for embedded google maps

NUM_DAYS_UNCHALLENGED_B4_APPROVED = 7

ENABLE_GOOGLE_ANALYTICS = False

MAINTENANCE_MODE = False #set to true to put the whole site into maintenace mode

PAGE_COLUMNS = 5 #number of columns in multiple column listing page

#EXCLUDED_ORGS_FROM_GOOGLE_ANALYTICS = [1]   # org id numbers

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_URL = '/static/'
COMPRESS_ROOT = os.path.join(PROJECT_ROOT, 'website', 'static')
COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter',
                        'compressor.filters.cssmin.CSSMinFilter']
COMPRESS_JS_FILTERS = ['compressor.filters.closure.ClosureCompilerFilter']
COMPRESS_CLOSURE_COMPILER_BINARY = '/usr/local/bin/closure'
COMPRESS_CLOSURE_COMPILER_ARGUMENTS = '--language_in ECMASCRIPT5 --summary_detail_level 3'
def COMPRESS_JINJA2_GET_ENVIRONMENT():
    from django_jinja.base import env
    return env

# do not run migrations during testing
SOUTH_TESTS_MIGRATE=False

FORUM_INTEGRATION=False

# django-tracking2
TRACK_AJAX_REQUESTS = True
TRACK_ANONYMOUS_USERS = True
TRACK_PAGEVIEWS = True
TRACK_IGNORE_URLS = ['tracking', 'admin']

# Jinja2 integration via django-jinja
DEFAULT_JINJA2_TEMPLATE_INTERCEPT_RE = r'.*(?:jinja|js)$'
JINJA2_EXTENSIONS = ['jinja2.ext.WithExtension',
                     'compressor.contrib.jinja2ext.CompressorExtension']

# django-autocomplete; has nothing to do with our current search autocomplete
AUTOCOMPLETE_MEDIA_PREFIX = '/static/autocomplete/'
AUTOCOMPLETE_JQUERY_ALREADY_INCLUDED = True

#
STATSD_TRACK_MIDDLEWARE = True

from settings_local import *

if DEBUG:
    INSTALLED_APPS += ('django_extensions',
                       'debug_toolbar')

_CANONICAL_SITE_URL = SITE_URL
try:
    _CANONICAL_SITE_URL = CANONICAL_SITE_URL
except:
    pass

# this has to be after we import settings_local, obviously
JINJA2_CONSTANTS = {
    'INTERNAL_IPS': INTERNAL_IPS,
    'ENABLE_GOOGLE_ANALYTICS': ENABLE_GOOGLE_ANALYTICS,
    'FORUM_INTEGRATION': FORUM_INTEGRATION,
    'CANONICAL_SITE_URL': _CANONICAL_SITE_URL,
}

try:
    FEEDBACK_EMAIL
except:
    FEEDBACK_EMAIL = "feedback@cleanpowerfinance.com"
