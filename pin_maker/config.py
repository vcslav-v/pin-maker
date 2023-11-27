import os
from loguru import logger


PINTEREST_LOGIN = os.environ.get('PINTEREST_LOGIN', '')   
PINTEREST_PASSWORD = os.environ.get('PINTEREST_PASSWORD', '')
DROP_PREFIX = 'temp-browser'
DO_TOKEN = os.environ.get('DO_TOKEN', '')
PB_LOGIN = os.environ.get('PB_LOGIN', '')
PB_PASSWORD = os.environ.get('PB_PASSWORD', '')
SITE_URL = os.environ.get('SITE_URL', '')
if os.environ.get('DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace(
        'postgres', 'postgresql+psycopg2'
    )
else:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:mysecretpassword@0.0.0.0/postgres'
DO_SPACE_BUCKET = os.environ.get('DO_SPACE_BUCKET', '')
DO_SPACE_REGION = os.environ.get('DO_SPACE_REGION', '')
DO_SPACE_ENDPOINT = os.environ.get('DO_SPACE_ENDPOINT', '')
DO_SPACE_KEY = os.environ.get('DO_SPACE_KEY', '')
DO_SPACE_SECRET = os.environ.get('DO_SPACE_SECRET', '')

STANDARD_TEMPLATE_NAME = 'std_template'
COLLAGE_TEMPLATE_NAME = 'collage_template'
PIN_DESCRIPTION_COUNT = 500
NESESSARY_DESC_COUNT = 100

MAIN_BOARD_NAME = os.environ.get('MAIN_BOARD_NAME', '')
FREEBIES_BOARD_NAME = os.environ.get('FREEBIES_BOARD_NAME', '')
PLUS_BOARD_NAME = os.environ.get('PLUS_BOARD_NAME', '')
PREMIUM_BOARD_NAME = os.environ.get('PREMIUM_BOARD_NAME', '')

REF_CODE = os.environ.get('REF_CODE', '')