from flask import Flask, request, session
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
app.secret_key = "super secret key"

users = {}

@app.route('/bot', methods=['POST'])
def bot():

    counter = session.get('counter', 0)
    counter += 1

    # Save the new counter value in the session
    session['counter'] = counter

    from_number = request.values.get('From')
    if from_number in users:
        name = users[from_number]
    else:
        name = "Friend"

    # Build our reply
    message = f'{name} has messaged '\
              f'{request.values.get("To")} '\
              f'{counter} times.'


    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    if 'quote' in incoming_msg:
        # return a quote
        r = requests.get('https://api.quotable.io/random')
        if r.status_code == 200:
            data = r.json()
            quote = f'{data["content"]} ({data["author"]})'
        else:
            quote = 'I could not retrieve a quote at this time, sorry.'
        msg.body(quote + " " + message)
        responded = True
    if 'cat' in incoming_msg:
        # return a cat pic
        msg.media('https://cataas.com/cat')
        msg.body(message)
        responded = True
    if not responded:
        msg.body('I only know about famous quotes and cats, sorry! ' + message)
    return str(resp)


if __name__ == '__main__':
    app.run()