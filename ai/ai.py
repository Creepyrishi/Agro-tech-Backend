## Dummy Prediction function

def predict_flammability(data):
    return 33


from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
import db

load_dotenv()

model = os.getenv('MODEL')
api = os.getenv('OPENAI_API')
client = OpenAI(base_url=os.getenv("BASE_URL_GROQ"), api_key=api)


def get_explanation(_id):
    document = db.get_chat(_id)
    conversation = document[0]['conversation']
    try:
        response = client.chat.completions.create( model=model, temperature=0.3, messages=conversation)
        return response.choices[0].message.content

    except Exception as e:
        return False
