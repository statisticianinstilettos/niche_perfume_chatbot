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

    if body == 'Tell me more':
        resp.message("Great! I love talking about my code! I use a Machine Learning model that scans tons of perfumes online to find your personalized recommendations. Read more about the model in this article. https://towardsdatascience.com/perfume-recommendations-using-natural-language-processing-ad3e6736074c")
  

    elif body == 'Goodbye':
        # Add a text message
        msg = resp.message("Hi. I've placed an auto-response chip in my brain so I can spend time with my family. Thank you for talking to Rick.")
        # Add a picture message
        msg.media("https://i0.wp.com/decider.com/wp-content/uploads/2020/05/rick-and-morty-copy.jpg?quality=80&strip=all&ssl=1")  

    else:
        resp.message("Hi! I'm a chatbot programmed to help you find your perfect signature perfume! To get started, just respond with a description of what you are looking for. Be as detailed as you want! The more information I have, the easier it is for me to compute your top matches. If you'd like to learn more about how I'm programmed respond with 'Tell me more'")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)


