from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route("/chatbot", methods=['GET', 'POST'])
def chatbot():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    """Respond to incoming calls with a MMS message."""
    # Start our TwiML response
    resp = MessagingResponse()

    if body == 'Hello':
        # Add a text message
        msg = resp.message("Hi. I've placed an auto-response chip in my brain so I can spend time with my family. Thank you for talking to Rick.")
        # Add a picture message
        msg.media("https://i0.wp.com/decider.com/wp-content/uploads/2020/05/rick-and-morty-copy.jpg?quality=80&strip=all&ssl=1")
   
    elif body == 'Bye':
        resp.message("Goodbye")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)


