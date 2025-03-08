
from flask import Flask, jsonify, request, redirect, url_for, session, g, flash, render_template
# from flask_oauth import OAuth
import requests
import urllib
from werkzeug.exceptions import BadRequest
from app.main.bot.chat import chat_handler
from app.main.tool_operations.utils import context
from app.main.tool_operations.auth import OAuth2Helper
import app.main.config as config

# configuration
SECRET_KEY = 'dev key'
DEBUG = True

# setup flask
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY


@app.route('/')
def index():
    """Index route"""
   
    return render_template(
        'index.html',
       
        title="QB Customer Leads",
    )


@app.route('/bot')
def bot():
    """bot route"""
    request_context = context.RequestContext(session['realm_id'], session['access_token'], session['refresh_token'])
    
    # print(get_historical_transactions(req_context=request_context))
    return render_template(
        'chat.html',
       
    )


    
@app.route('/auth')
def auth():
    """Initiates the Authorization flow after getting the right config value"""
    params = {
        'scope': 'com.intuit.quickbooks.accounting', 
        'redirect_uri': config.REDIRECT_URI,
        'response_type': 'code', 
        'client_id': config.CLIENT_ID,
        'state': csrf_token()
    }
    url = OAuth2Helper.get_discovery_doc()['authorization_endpoint'] + '?' + urllib.parse.urlencode(params)
    return redirect(url)
   
@app.route('/reset-session')
def reset_session():
    """Resets session"""
    session.pop('qbo_token', None)
    session['is_authorized'] = False
    return redirect(request.referrer or url_for('index'))

@app.route('/callback')
def callback():
    """Handles callback only for OAuth2"""
    #session['realmid'] = str(request.args.get('realmId'))
    state = str(request.args.get('state'))
    error = str(request.args.get('error'))
    if error == 'access_denied':
        return redirect(index)
    if state is None:
        return BadRequest()
    elif state != csrf_token():  # validate against CSRF attacks
        return BadRequest('unauthorized')
    
    auth_code = str(request.args.get('code'))
    if auth_code is None:
        return BadRequest()
    
    bearer = OAuth2Helper.get_bearer_token(auth_code)
    realmId = str(request.args.get('realmId'))

    # update session here
    session['is_authorized'] = True 
    session['realm_id'] = realmId
    session['access_token'] = bearer['access_token']
    session['refresh_token'] = bearer['refresh_token']

    return redirect(url_for('index'))

def csrf_token():
    token = session.get('csrfToken', None)
    if token is None:
        token = OAuth2Helper.secret_key()
        session['csrfToken'] = token
    return token


@app.route('/chat', methods=['POST'])
def handle_chat():
    """Handle chat messages from the user"""
    data = request.json
    user_message = data.get('message', '')
    
    # Get session from request context
    req_context = get_request_context()
    
    # Process message with chat handler
    response = chat_handler(req_context, user_message)
    
    return jsonify({
        'response': response
    })
    
    

def get_request_context():
    """Get request context with authentication info"""
    from collections import namedtuple
    
    # Create a simple context object with necessary authentication info
    RequestContext = namedtuple('RequestContext', ['access_token', 'realm_id'])
    
    # Get access token and realm ID from session
    access_token = session.get('access_token')
    realm_id = session.get('realm_id')
    
    return RequestContext(access_token=access_token, realm_id=realm_id)

if __name__ == '__main__':
    app.run()
