import os
from airtable import Airtable
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv, find_dotenv
from src.information_retrieval_model import Perfume_Information_Retrieval_Model
load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = "super secret key"

AIRTABLE_BASE_ID = os.environ['AIRTABLE_BASE_ID']
AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']

# Load ML model 
model = Perfume_Information_Retrieval_Model()


@app.route('/send-survey', methods=['POST'])
def send_survey():
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
      session[sender_phone_number]['Number'] = twilio_phone_number
      #make response
      sms_message = "Hi! I'm a chatbot programmed to help you find your perfect signature perfume! To get started, just respond with a description of what you are looking for. Be as detailed as you want!"
      msg.body(sms_message)
       
    elif sms_count == 1:
      #update airtable 
      session[sender_phone_number]['Score'] = request_body

      #Get recs from ML
      recs = model.query_similar_perfumes(request_body, 1)
      perfume_name = recs.index[0]
      perfume_score = round(recs.iloc[0].ensemble_similarity,4)
      #perfume_image = 
      #perfume_link = 

      sms_message = "Great! Here are your top recommendation. {}. Match score = {}".format(perfume_name, perfume_score)
      msg.body(sms_message)
      msg.media("https://static.luckyscent.com/images/products/511056.jpg?width=400&404=product.png")  

      #update airtable with predictions and scores
      session[sender_phone_number]['Reason'] = request_body

      
    elif sms_count == 2:
      session[sender_phone_number]['Reason'] = request_body
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





@app.route('/get-scores', methods=['GET'])
def get_scores():
   phone_number = str(request.args.get('number'))

   airtable = Airtable(base_key=AIRTABLE_BASE_ID, table_name='Input', api_key=AIRTABLE_API_KEY)
   airtable_data_dict = {}
   score_list = []

   for page in airtable.get_iter(view='nps', filterByFormula="({Number}=" + phone_number + ")"):
       for record in page:
           num_id = record['fields']['ID']
           airtable_data_dict[num_id] = {}
           airtable_data_dict[num_id]['score'] = record['fields']['Score']
           airtable_data_dict[num_id]['reason'] = record['fields']['Reason']
           airtable_data_dict[num_id]['comments'] = record['fields']['Comments']

   return {'overallNPS': nps_total_score, 'airtableData': airtable_data_dict}

if __name__ == "__main__":
    app.run(debug=True)

