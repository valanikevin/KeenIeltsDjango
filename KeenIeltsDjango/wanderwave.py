from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI
from django.conf import settings
import os
import json


@api_view(['POST'])
def generate_itinerary(request):
    data = eval(request.body.decode('utf-8'))
    i_response = openai_generate_itinerary(data)

    return Response(data=i_response, status=200)


def openai_generate_itinerary(data):
    OPENAI_KEY = settings.OPENAI_SECRET
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY
    chat_model = ChatOpenAI(
        temperature=0.6, model_name="gpt-3.5-turbo-16k")

    ITINERARY_PROMPT = f"""
    You are a travel itinerary generator. You are given a list of cities and a list of activities. You must generate an itinerary for the traveler. The itinerary must include the cities and activities in the list. The itinerary must be in the order.
    
    User Input:
    From City: {data.get("fromCity")}
    Destination Cities: {data["destinationCity"]}
    Date: {data["date"]}
    Number of Days: {data["days"]}
    Budget: {data["budget"]}
    Activities/Notes from Traveller: {data["tripRequirements"]}

    - Suggest traveller all the hidden and interesting places they should visit between the from city and destination cities. Your job is to make traveler trip very interesting and memorable.
    - You should include at least 8-10 items in the itinerary.
    - Your response should include JSON list of arrays with these keys: city (string), activity (string, 50-100 words), date (string), special_attractions (string, 50-100 words).
    Sample Response:
    {{
        "itinerary": [{{}}, {{}}, {{}},]
    }}
    """

    message = [SystemMessage(content=ITINERARY_PROMPT)]
    response = json.loads(chat_model.invoke(message).content)

    return response
