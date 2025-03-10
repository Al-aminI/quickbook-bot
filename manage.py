
import json
from flask import Flask, jsonify, request, redirect, url_for, session, g, flash, render_template, Response
import time
import requests
import urllib
from werkzeug.exceptions import BadRequest
from app.main.bot.chat import chat_handler
from app.main.tool_operations.utils import context
from app.main.tool_operations.auth import OAuth2Helper
import app.main.config as config
import uuid
from collections import deque
import threading

# configuration
SECRET_KEY = 'dev key'
DEBUG = True

# setup flask
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
response_queues = {}
response_lock = threading.Lock()


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
 

    return render_template(
        'chat.html',
       
    )

@app.route('/bot-stream')
def bot_stream():
    """bot stream route"""
   
  
    return render_template(
        'chat-stream.html',
       
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
    if not isinstance(response, str):
        response = response.content

    return jsonify({
        'response': response
    })
#   # Server-Sent Events implementation that supports both methods
# @app.route('/stream-chat', methods=['GET', 'POST'])
# def stream_chat():
#     """Stream chat responses using Server-Sent Events"""
    
#     # Handle the POST request - process the message and queue response chunks
#     if request.method == 'POST':
#         data = request.json
#         user_message = data.get('message', '')
#         client_id = data.get('client_id', str(uuid.uuid4()))
        
#         # Get session from request context
#         req_context = get_request_context()
        
#         # Create a new response queue for this request
#         with response_lock:
#             response_queues[client_id] = deque()
        
#         # Process message with chat handler in a separate thread
#         def process_message():
#             try:
#                 # Process message with chat handler
#                 response = chat_handler(req_context, user_message)
                
#                 if not isinstance(response, str):
#                     response = response.content
                
#                 # Split response into chunks
#                 chunks = simulate_streaming(response)
                
#                 # Queue the chunks for retrieval via SSE
#                 with response_lock:
#                     if client_id in response_queues:
#                         queue = response_queues[client_id]
#                         for chunk in chunks:
#                             queue.append(chunk)
#                         # Add end marker
#                         queue.append(None)
#             except Exception as e:
#                 # Handle any errors
#                 with response_lock:
#                     if client_id in response_queues:
#                         response_queues[client_id].append(f"Error: {str(e)}")
#                         response_queues[client_id].append(None)  # End marker
        
#         # Start processing in background
#         threading.Thread(target=process_message).start()
        
#         # Return the client ID to be used for the SSE connection
#         return jsonify({
#             'client_id': client_id
#         })
    
#     # Handle the GET request - establish SSE connection and stream responses
#     elif request.method == 'GET':
#         # Get client ID from query parameter
#         client_id = request.args.get('client_id')
        
#         if not client_id or client_id not in response_queues:
#             return jsonify({'error': 'Invalid or missing client ID'}), 400
        
#         def generate():
#             """Generator function for SSE"""
#             try:
#                 # Send event to mark the start of the response
#                 yield 'event: start\ndata: Starting response\n\n'
                
#                 # Keep checking the queue until we get the end marker (None)
#                 while True:
#                     # Check if there are chunks available
#                     with response_lock:
#                         if client_id in response_queues and response_queues[client_id]:
#                             chunk = response_queues[client_id].popleft()
                            
#                             # If we get the end marker, break the loop
#                             if chunk is None:
#                                 break
                            
#                             # Send the chunk
#                             data = json.dumps({'chunk': chunk})
#                             yield f'data: {data}\n\n'
                    
#                     # Short sleep to prevent CPU spinning
#                     time.sleep(0.05)
                
#                 # Send event to mark the end of the response
#                 yield 'event: end\ndata: Response complete\n\n'
                
#                 # Clean up the queue
#                 with response_lock:
#                     if client_id in response_queues:
#                         del response_queues[client_id]
                        
#             except GeneratorExit:
#                 # Client disconnected, clean up
#                 with response_lock:
#                     if client_id in response_queues:
#                         del response_queues[client_id]
        
#         return Response(generate(), mimetype='text/event-stream')


@app.route('/stream-chat', methods=['GET', 'POST'])
def stream_chat():
    """Stream chat responses using Server-Sent Events"""
    
    # Handle the POST request - process the message and queue response chunks
    if request.method == 'POST':
        data = request.json
        user_message = data.get('message', '')
        client_id = data.get('client_id', str(uuid.uuid4()))
        
        # Get session from request context
        req_context = get_request_context()
        
        # Create a new response queue for this request
        with response_lock:
            response_queues[client_id] = deque()
        
        # Process message with chat handler in a separate thread
        def process_message():
            try:
                # Process message with chat handler
                for response_chunk in chat_handler(req_context, user_message):
                    # Queue each yielded chunk directly
                    with response_lock:
                        if client_id in response_queues:
                            response_queues[client_id].append(response_chunk)
                
                # Add end marker
                with response_lock:
                    if client_id in response_queues:
                        response_queues[client_id].append(None)
            except Exception as e:
                # Handle any errors
                with response_lock:
                    if client_id in response_queues:
                        response_queues[client_id].append(f"Error: {str(e)}")
                        response_queues[client_id].append(None)  # End marker
        
        # Start processing in background
        threading.Thread(target=process_message).start()
        
        # Return the client ID to be used for the SSE connection
        return jsonify({
            'client_id': client_id
        })
    
    # Handle the GET request - establish SSE connection and stream responses
    elif request.method == 'GET':
        # Get client ID from query parameter
        client_id = request.args.get('client_id')
        
        if not client_id or client_id not in response_queues:
            return jsonify({'error': 'Invalid or missing client ID'}), 400
        
        def generate():
            """Generator function for SSE"""
            try:
                # Send event to mark the start of the response
                yield 'event: start\ndata: Starting response\n\n'
                
                # Keep checking the queue until we get the end marker (None)
                while True:
                    # Check if there are chunks available
                    with response_lock:
                        if client_id in response_queues and response_queues[client_id]:
                            chunk = response_queues[client_id].popleft()
                            
                            # If we get the end marker, break the loop
                            if chunk is None:
                                break
                            
                            # Send the chunk
                            data = json.dumps({'chunk': chunk})
                            yield f'data: {data}\n\n'
                    
                    # Short sleep to prevent CPU spinning
                    time.sleep(0.05)
                
                # Send event to mark the end of the response
                yield 'event: end\ndata: Response complete\n\n'
                
                # Clean up the queue
                with response_lock:
                    if client_id in response_queues:
                        del response_queues[client_id]
                        
            except GeneratorExit:
                # Client disconnected, clean up
                with response_lock:
                    if client_id in response_queues:
                        del response_queues[client_id]
        
        return Response(generate(), mimetype='text/event-stream')

def simulate_streaming(text):
    """Helper function to simulate streaming by breaking text into chunks"""
    words = text.split()
    chunks = []
    
    # Create chunks of ~5 words each
    for i in range(0, len(words),2):
        chunk = ' '.join(words[i:i+2])
        if i + 2 < len(words):
            chunk += ' '  # Add space if not the last chunk
        chunks.append(chunk)
    
    return chunks



    

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
