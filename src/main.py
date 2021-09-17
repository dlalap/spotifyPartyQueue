from flask import Flask, request, redirect, session
from twilio.twiml.messaging_response import MessagingResponse
from model.mainClass import Spot
from model.users import User
import json

app = Flask(__name__)
app.secret_key = "super secret key"
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
    log_user(from_number)

    # # Build our reply
    # message = f'{name} has messaged '\
    #           f'{request.values.get("To")} '\
    #           f'{counter} times.'

    # Put it in a TwiML response
    # resp = MessagingResponse()
    # resp.message(message)

    # return str(resp)
        
def log_user(from_number):
    if from_number in users:
        name = users[from_number]
    else:
        name = f"Friend_{from_number}"
        users[from_number] = User(name, from_number)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    counter = session.get('counter', 0)
    counter += 1

    # Save the new counter value in the session
    session['counter'] = counter

    from_number = request.values.get('From')
    log_user(from_number)

    currentUser = users[from_number]
    body = request.values.get('Body', None)
    if body is None:
        return

    print(request)

    # Handle message
    resp = None
    respMessage = None

    # Handle controls
    if body == '$NEXT':
        spotQueue.NextSong()
        msg = "Playing next song in queue!"
        resp = MessagingResponse()
        resp.message(msg)
        return str(resp)
    else:
        
        
        # if user already searched for results, return first 5 results
        # SHOW FIRST FIVE RESULTS
        if currentUser.get_search_results() is not None:
            if body == "0":
                msg = spotQueue.listSongNameAndArtists(currentUser.get_search_results_range(5, 10), 5)
                resp = MessagingResponse()
                resp.message(msg)
                return str(resp)


            if body.isnumeric():
                if int(body) > 0 and int(body) < 11:
                    options = currentUser.get_search_results()
                    selected = options[int(body) - 1]
                    songUri = selected['uri']
                    songName = selected['name']
                    songArtists = spotQueue.listAllArtistsInResult(selected)
                    spotQueue.addSongsToPlaylist(songUri)
                    msg = f"Adding {songName} by {songArtists} to the playlist."
                    resp = MessagingResponse()
                    resp.message(msg)
                    currentUser.clear_search_results()
                    currentUser.set_stage(0)
                    return str(resp)

        # any number 1 to 5 corresponds to song selection
        # LISTEN FOR SONG SELECTION

        # if 0 (next) selected, return last 5 results
        # SHOW LAST FIVE RESULTS

        # any number 6 to 10 corresponds to song selection
        # LISTEN FOR SONG SELECTION

        # typing any words goes to song search and replaces cached search
        # and automatically shows first 5 results
        # ELSE QUERY

        query = spotQueue.multiQuery(body, 10)
        currentUser.set_search_results(query)

        msg = spotQueue.listSongNameAndArtists(currentUser.get_search_results_range(0, 5))
        if len(currentUser.get_search_results()) > 5:
            msg += "\n Press 0 for more results"
        else:
            msg += "\n No more results"
        resp = MessagingResponse()
        resp.message(msg)
        return str(resp)


    # return report_song_added_to_playlist(resp)
   

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
