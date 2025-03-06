
from flask import Flask, request, redirect, url_for, session, g, flash, render_template
# from flask_oauth import OAuth
import requests
import urllib
from werkzeug.exceptions import BadRequest
from app.main.tools.service.customer import create_customer
from app.main.tools.service.company import get_companyInfo
from app.main.tools.service.transaction import get_historical_transactions, get_uncategorized_transactions, categorize_transaction
from app.main.tools.utils import context
from app.main.tools.auth import OAuth2Helper
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



@app.route('/company-info')
def company_info():
    """Gets CompanyInfo of the connected QBO account"""
    request_context = context.RequestContext(session['realm_id'], session['access_token'], session['refresh_token'])
    
    # print(get_historical_transactions(req_context=request_context, keyword='Books'))
    # print(get_uncategorized_transactions(req_context=request_context))
    print(categorize_transaction(req_context=request_context, transaction_id=64, category="food"))
    
    response = get_companyInfo(request_context)
    if (response.status_code == 200):
        return render_template(
            'index.html',
            
            company_info='Company Name: ' + response.json()['CompanyInfo']['CompanyName'],
            title='QB Customer Leads',
        )
    else:
        return render_template(
            'index.html',
         
            company_info=response.text,
            title='QB Customer Leads',
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

if __name__ == '__main__':
    app.run()
