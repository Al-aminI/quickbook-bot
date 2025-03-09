DEBUG = False
SQLALCHEMY_ECHO = False

# OAuth2 credentials
CLIENT_ID= ''
CLIENT_SECRET = ''
# REDIRECT_URI = 'https://vksplgr2-5000.uks1.devtunnels.ms/callback'
REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_TYPE='OAuth2'
# Choose environment; default is sandbox
ENVIRONMENT = 'Sandbox'
# ENVIRONMENT = 'Production'

# Set to latest at the time of updating this app, can be be configured to any minor version
API_MINORVERSION = '75'

GOOGLE_AI_API_KEY=""
OPEN_AI_API_KEY=""