from flask import Flask, request, redirect, session
from twilio.twiml.messaging_response import MessagingResponse
from model.mainClass import Spot
import json

app = Flask(__name__)
spotQueue = Spot()
users = {}

@app.route("/", methods=['GET', 'POST'])
def hello():
    """Respond with the number of text messages sent between two parties."""
    # Increment the counter
    counter = session.get('counter', 0)
    counter += 1

    # Save the new counter value in the session
    session['counter'] = counter

    from_number = request.values.get('From')
    if from_number in users:
        name = callers[from_number]
    else:
        name = "Friend"

    # Build our reply
    message = f'{name} has messaged '\
              f'{request.values.get("To")} '\
              f'{counter} times.'

    # Put it in a TwiML response
    resp = MessagingResponse()
    resp.message(message)

    return str(resp)
        


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    print(request)

    # Handle message
    resp = None
    respMessage = None
    if body is not None:
        if body == '$NEXT':
            spotQueue.NextSong()
            msg = "Playing next song in queue!"
            resp = MessagingResponse()
            resp.message(msg)
            return str(resp)
        else:
            resp = spotQueue.singleQuery(body)

    return report_song_added_to_playlist(resp)
   


def report_song_added_to_playlist(response_dict):
    if response_dict is None:
        return None
    songName = response_dict['name']
    songArtist = response_dict['artists'][0]['name']
    message = (
        f'Adding {songName} '
        f'by {songArtist} to playlist "Rolling Queue."'
    ) 
    #return message
    resp = MessagingResponse()
    resp.message(message)
    return str(resp)

@app.route("/monitor", methods=['GET'])
def toggle_monitor():
    monitorActive = spotQueue.toggleSongMonitor()
    
    if monitorActive:
        return "Song monitor is active. Removing current playbacks from queue."
    else:
        return "Song monitor inactive."

@app.route("/hello", methods=['GET'])
def say_hi():
    spotQueue.ToggleTimer()
    return "Testing hello."

@app.route('/jsontest', methods=['GET'])
def json_test():
    json_payload = {
        'first': 'one',
        'second': 'two',
        'third': 'three',
        'fourth': 4
    }
    json_string = json.dumps(json_payload)
    # back_to_json = json.loads(json_string)

    print(json_payload)
    return json_string

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="1812", debug=True)
