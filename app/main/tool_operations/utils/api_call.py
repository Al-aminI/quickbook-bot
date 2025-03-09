# api_call.py


import requests
from requests_oauthlib import OAuth1
import app.main.config as config
import json

def get_request(req_context, uri, params):
    """HTTP GET request for QBO API"""
    headers = { 'Accept': "application/json", 
        'User-Agent': "PythonSampleApp1"
    }
    pos = uri.find("v3")
    if pos == -1:
        raise ValueError("The URL does not contain 'v3'")
    
    substring = uri[pos:]
    url = (substring
       .replace("{{companyid}}", req_context.realm_id)
       .replace("{companyid}", req_context.realm_id)
       .replace("{{minorversion}}", config.API_MINORVERSION))

    if config.ENVIRONMENT == "Sandbox":
        base_url = "https://sandbox-quickbooks.api.intuit.com/"
    else:
        base_url = "https://quickbooks.api.intuit.com/"
    url = base_url + url

    if config.AUTH_TYPE == "OAuth2":
        headers['Authorization'] = "Bearer " + req_context.access_token
        req = requests.get(url, headers=headers, params=params)
     
    else:
        auth = OAuth1(req_context.consumer_key, req_context.consumer_secret, req_context.access_key, req_context.access_secret)
        req = requests.get(url, auth=auth, headers=headers)
    return req

def post_request(req_context, uri, payload):
    """HTTP POST request for QBO API"""
    headers = { 'Accept': "application/json", 
        'content-type': "application/json; charset=utf-8", 
        'User-Agent': "PythonSampleApp1"
    }
    
    pos = uri.find("v3")
    if pos == -1:
        raise ValueError("The URL does not contain 'v3'")
    
    substring = uri[pos:]
    url = (substring
       .replace("{{companyid}}", req_context.realm_id)
       .replace("{companyid}", req_context.realm_id)
       .replace("{{minorversion}}", config.API_MINORVERSION))

    if config.ENVIRONMENT == "Sandbox":
        base_url = "https://sandbox-quickbooks.api.intuit.com/"
    else:
        base_url = "https://quickbooks.api.intuit.com/"
    url = base_url + url
    
    if config.AUTH_TYPE == "OAuth2":
        headers['Authorization'] = "Bearer " + req_context.access_token
        req = requests.post(url, headers=headers, data=json.dumps(payload))
        print(req.text)
    else:
        auth = OAuth1(req_context.consumer_key, req_context.consumer_secret, req_context.access_key, req_context.access_secret)
        req = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload))
        
    return req




    
        
