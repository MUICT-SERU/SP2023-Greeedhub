"""Settings module."""
import os


USE_COMBINED = os.getenv('ACCESSLOG_USE_COMBINED', 'False')

IS_COMBINED = USE_COMBINED.lower() == 'true'
