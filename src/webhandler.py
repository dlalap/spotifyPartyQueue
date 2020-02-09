from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from model.mainClass import Spot
import json

app = Flask(__name__)
spotQueue = Spot()


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    # resp = MessagingResponse()

    # Determine the right reply for this message
    # if body == 'hello':
    #     resp.message("Hello there, person!")
    # elif body == 'bye':
    #     resp.message("Farewell.")
    resp = None
    respMessage = None
    if body is not None:
        if body == '$NEXT':
            spotQueue.NextSong()
        else:
            resp = spotQueue.singleQuery(body)

    if resp is not None:
        songName = resp['name']
        songArtist = resp['artists'][0]['name']
        respMessage = (
            f"Adding {songName} "
            f"by {songArtist} to queue playlist."
        )

    return respMessage

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

    print(json.loads(json_string))
    return json_string

if __name__ == "__main__":
    app.run(debug=True)
