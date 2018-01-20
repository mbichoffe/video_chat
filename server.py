import os
from flask import Flask, jsonify, request
from faker import Factory
from twilio.rest import Client
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import (
    SyncGrant,
    VideoGrant,
    ChatGrant
)
from dotenv import load_dotenv, find_dotenv
from os.path import join, dirname
from inflection import underscore

app = Flask(__name__)
fake = Factory.create()
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app.secret_key = "AIRSPEEDVELOCITYOFANUNLADENSWALLOW"


# Basic health check - check environment variables have been configured
# correctly
@app.route('/config')
def config():
    return jsonify(
        TWILIO_ACCOUNT_SID=os.environ['TWILIO_ACCOUNT_SID'],
        TWILIO_NOTIFICATION_SERVICE_SID=os.environ.get('TWILIO_NOTIFICATION_SERVICE_SID', None),
        TWILIO_API_KEY=os.environ['TWILIO_API_KEY'],
        TWILIO_API_SECRET=bool(os.environ['TWILIO_API_SECRET']),
        TWILIO_CHAT_SERVICE_SID=os.environ.get('TWILIO_CHAT_SERVICE_SID', None),
        TWILIO_SYNC_SERVICE_SID=os.environ.get('TWILIO_SYNC_SERVICE_SID', 'default'),
    )


@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/video/')
def video():
    return app.send_static_file('video/index.html')

@app.route('/chat/')
def chat():
    return app.send_static_file('chat/index.html')


@app.route('/token', methods=['GET'])
def randomToken():
    return generateToken(fake.user_name())


@app.route('/token', methods=['POST'])
def createToken():
    # Get the request json or form data
    content = request.get_json() or request.form
    # get the identity from the request, or make one up
    identity = content.get('identity', fake.user_name())
    return generateToken(identity)

@app.route('/token/<identity>', methods=['POST', 'GET'])
def token(identity):
    return generateToken(identity)

def generateToken(identity):
    # get credentials for environment variables
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    api_key = os.environ['TWILIO_API_KEY']
    api_secret = os.environ['TWILIO_API_SECRET']
    sync_service_sid = os.environ.get('TWILIO_SYNC_SERVICE_SID', 'default')
    chat_service_sid = os.environ.get('TWILIO_CHAT_SERVICE_SID', None)

    # Create access token with credentials
    token = AccessToken(account_sid, api_key, api_secret, identity=identity)

    # Create a Sync grant and add to token
    if sync_service_sid:
        sync_grant = SyncGrant(service_sid=sync_service_sid)
        token.add_grant(sync_grant)

    # Create a Video grant and add to token
    video_grant = VideoGrant()
    token.add_grant(video_grant)

    # Create an Chat grant and add to token
    if chat_service_sid:
        chat_grant = ChatGrant(service_sid=chat_service_sid)
        token.add_grant(chat_grant)

    # Return token info as JSON
    return jsonify(identity=identity, token=token.to_jwt().decode('utf-8'))

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

# Ensure that the Sync Default Service is provisioned
def provision_sync_default_service():
    client = Client(os.environ['TWILIO_API_KEY'], os.environ['TWILIO_API_SECRET'], os.environ['TWILIO_ACCOUNT_SID'])
    client.sync.services('default').fetch()

if __name__ == '__main__':
    provision_sync_default_service()
    app.run(debug=True, port=5001)
