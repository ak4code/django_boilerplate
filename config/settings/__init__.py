import os

from split_settings.tools import include

include(
    'base.py',
)

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
if ENVIRONMENT == 'prod':
    include('prod.py')
else:
    include('dev.py')
