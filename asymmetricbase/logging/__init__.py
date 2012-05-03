import logging
from django.conf import settings

logger = logging.getLogger(getattr(settings, 'ASYM_LOGGER',  'asymm_logger'))
