# Copy this file to configure email without committing secrets.
# This file is loaded by app.py if present.

import os

# Toggle Gmail mailer (recommended)
GMAIL_ENABLED = True
GMAIL_EMAIL = 'manismansuri24@gmail.com'
GMAIL_PASSWORD = 'jscl afnw eeep meqs'  # App password; spaces will be removed automatically

# Optional: environment-driven
# GMAIL_ENABLED = os.getenv('GMAIL_ENABLED', 'False') == 'True'
# GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
# GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')

