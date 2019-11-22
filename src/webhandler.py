from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from model.mainClass import Spot

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
    if body is not None:
        resp = spotQueue.singleQuery(body)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
