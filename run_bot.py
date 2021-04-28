import os
from airtable import Airtable
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv, find_dotenv
from src.information_retrieval_model import Perfume_Information_Retrieval_Model
import pandas as pd 
import emoji
load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = "super secret key"

AIRTABLE_BASE_ID = os.environ['AIRTABLE_BASE_ID']
AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']

# Load ML model 
model = Perfume_Information_Retrieval_Model()
df = pd.read_pickle("data/perfume_data.pkl")


@app.route('/run-bot', methods=['POST'])
def run_bot():
   airtable = Airtable(base_key=AIRTABLE_BASE_ID, table_name='Input', api_key=AIRTABLE_API_KEY)
   request_body = request.values.get('Body', 'message error').lower()
   sender_phone_number = request.values.get('From', 'unknown_sender')
   twilio_phone_number = request.values.get('To', 'unknown_number')

   # reset session
   if 'reset' in request_body:
       del session['sms_count']
       session.pop(sender_phone_number, None)
       return("resetting the session")
      
   if not 'sms_count' in session:  
       session['sms_count'] = 0
       session[sender_phone_number] = {}

   #craft your response
   sms_count = session['sms_count']
   resp = MessagingResponse()
   msg = resp.message()

   if sms_count >= 0 and sms_count <= 2:
    if sms_count == 0:
      #update airtable
      session[sender_phone_number]['Number'] = sender_phone_number
      #make responses
      sms_message = "Hi there! I'm a chatbot programmed to help you find your perfect signature perfume! To get started, just respond with a description of what you are looking for. Be as detailed as you want!"
      msg.body(sms_message)
       
    elif sms_count == 1:
      #update airtable 
      session[sender_phone_number]['Query'] = request_body

      #Get recs from ML model
      recs = model.query_similar_perfumes(request_body, 3)
      
      #format recommendation 1
      perfume_name = recs.index.tolist()[0]
      perfume_score = round(recs.iloc[0].ensemble_similarity,4)
      perfume_notes = df.query('title==@perfume_name').notes.values[0]
      perfume_image = df.query('title==@perfume_name').image_url.values[0]
      shopping_link = "https://www.google.com/search?q=" + perfume_name.replace(" ", "+")
      sms_message = emoji.emojize("Great! Here are your top recommendation. :cherry_blossom: {} (match score={}). It was recommended because it has notes of {}. Shop for it here {}. \n ".format(perfume_name, perfume_score, perfume_notes, shopping_link))
      msg.media(perfume_image)  

      #format recommendation 2
      perfume_name = recs.index.tolist()[1]
      perfume_score = round(recs.iloc[1].ensemble_similarity,4)
      perfume_notes = df.query('title==@perfume_name').notes.values[0]
      perfume_image = df.query('title==@perfume_name').image_url.values[0]
      shopping_link = "https://www.google.com/search?q=" + perfume_name.replace(" ", "+")
      sms_message = sms_message + emoji.emojize("You can also try :mushroom: {} (match score={}). Notes are {}. Shop it here {}. \n".format(perfume_name, perfume_score, perfume_notes, shopping_link))
     
      #format recommendation 3
      perfume_name = recs.index.tolist()[2]
      perfume_score = round(recs.iloc[2].ensemble_similarity,4)
      perfume_notes = df.query('title==@perfume_name').notes.values[0]
      perfume_image = df.query('title==@perfume_name').image_url.values[0]
      shopping_link = "https://www.google.com/search?q=" + perfume_name.replace(" ", "+")
      sms_message = sms_message + emoji.emojize(" Or try :bouquet: {} (match score={}). Notes are {}. Shop it here {}. Enjoy!".format(perfume_name, perfume_score, perfume_notes, shopping_link))
      sms_message = sms_message + emoji.emojize(":red_heart:")
      msg.body(sms_message)
      
      #update airtable with predictions and scores
      session[sender_phone_number]['Predictions'] = sms_message
      airtable.insert(session[sender_phone_number])

      
    elif sms_count == 2:
      sms_message = "Thanks and enjoy your new perfume! If you want new recommendations, just type 'Reset' to start over."
      msg.body(sms_message)
      
    session['sms_count'] += 1

   else:
    if request_body == "more":
      sms_message = "Great! I love talking about my code! I use a Machine Learning model that scans tons of perfumes online to find your personalized recommendations. Read more about the model in this article. https://towardsdatascience.com/perfume-recommendations-using-natural-language-processing-ad3e6736074c"
      msg.body(sms_message)
    else:
      sms_message = "Hi. I've placed an auto-response chip in my brain so I can spend time with my family. Thank you for talking to Rick. Type 'Reset' to start over. If you want to learn more about how I'm programmed type 'More'. "
      msg.body(sms_message)
      msg.media("https://i0.wp.com/decider.com/wp-content/uploads/2020/05/rick-and-morty-copy.jpg?quality=80&strip=all&ssl=1")  

   return str(resp)



if __name__ == "__main__":
    app.run(debug=True)

