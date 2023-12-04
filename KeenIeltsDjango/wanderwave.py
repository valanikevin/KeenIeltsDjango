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
    try:
        i_response = openai_generate_itinerary(data)
    except Exception as e:
        print(e)
        sample_itinerary = {"itinerary": [
            {
                "city": "Edmonton (AB)",
                "activity": "Arrive in Edmonton and check into a cozy cabin or lodge in the mountains. Enjoy the peaceful and scenic surroundings. Explore the local cuisine and try some delicious dishes at a nearby restaurant. Take a leisurely walk around the area and soak in the tranquility. Spend the evening relaxing and enjoying the mountain views.",
                "date": "Dec 20, 2023",
                "special_attractions": "Visit Elk Island National Park, located just outside of Edmonton. This park is home to a variety of wildlife, including elk, bison, and more. Take a wildlife viewing tour and spot these majestic creatures in their natural habitat. Enjoy the serene beauty of the park and capture some stunning photographs."
            },
            {
                "city": "Banff (AB)",
                "activity": "Travel from Edmonton to Banff, a charming town nestled in the heart of the Canadian Rockies. Check into your accommodation and take a stroll around the town. Visit the Banff Park Museum, which showcases the natural history of the region. Enjoy a scenic drive along the Bow Valley Parkway and stop at Johnston Canyon to marvel at the stunning waterfalls. In the evening, dine at a local restaurant and savor the flavors of the Rocky Mountains.",
                "date": "Dec 21, 2023",
                "special_attractions": "Explore the Banff National Park, known for its breathtaking landscapes and abundant wildlife. Take a hike to Lake Louise and be mesmerized by the turquoise waters surrounded by snow-capped mountains. Visit the Fairmont Banff Springs Hotel, a historic and luxurious mountain resort. Take a dip in the Banff Upper Hot Springs and relax in the warm mineral-rich waters while enjoying panoramic views of the mountains."
            },
            {
                "city": "Banff (AB)",
                "activity": "Embark on a wildlife safari tour and spot animals such as bears, elk, and bighorn sheep. Take a scenic gondola ride to the top of Sulphur Mountain and enjoy panoramic views of the surrounding mountains. Visit the Cave and Basin National Historic Site, where you can learn about the history of the national parks in Canada. In the evening, dine at a mountain lodge and indulge in a delicious meal featuring local ingredients.",
                "date": "Dec 22, 2023",
                "special_attractions": "Take a helicopter tour over the Canadian Rockies and witness the breathtaking beauty from above. Visit the Banff Centre for Arts and Creativity, a renowned arts institution that hosts various exhibitions and performances. Explore the charming streets of Banff and browse through the boutiques and art galleries. Enjoy a scenic drive to Moraine Lake and marvel at its stunning turquoise waters."
            },
            {
                "city": "Jasper (AB)",
                "activity": "Travel from Banff to Jasper, a picturesque town surrounded by mountains and glaciers. Check into your accommodation and explore the town. Visit the Jasper SkyTram and ride to the top of Whistlers Mountain for panoramic views of the surrounding peaks. Take a leisurely walk along the shores of Pyramid Lake and enjoy the tranquility of nature. In the evening, dine at a cozy restaurant and savor the flavors of the Canadian Rockies.",
                "date": "Dec 23, 2023",
                "special_attractions": "Explore the Jasper National Park, a UNESCO World Heritage Site known for its stunning landscapes and diverse wildlife. Take a hike to the Athabasca Falls and witness the powerful cascades. Visit the Maligne Canyon and marvel at its deep limestone gorge. Take a boat tour on Maligne Lake and admire the breathtaking scenery. Keep an eye out for wildlife such as moose, elk, and mountain goats."
            },
            {
                "city": "Jasper (AB)",
                "activity": "Embark on a wildlife tour and spot animals such as bears, wolves, and caribou. Take a scenic drive along the Icefields Parkway and marvel at the glaciers and turquoise lakes. Visit the Columbia Icefield and take a guided tour onto the Athabasca Glacier. Explore the charming town of Jasper and browse through the local shops and art galleries. In the evening, dine at a mountain lodge and enjoy a delicious meal featuring local ingredients.",
                "date": "Dec 24, 2023",
                "special_attractions": "Take a scenic hike to the Valley of the Five Lakes and admire the stunning colors of the lakes. Visit the Jasper Park Lodge, a luxurious mountain resort with beautiful views of the surrounding mountains and lakes. Take a dip in the Miette Hot Springs and relax in the warm mineral-rich waters. Enjoy a horseback riding adventure and explore the scenic trails of the Canadian Rockies."
            },
            {
                "city": "Jasper (AB)",
                "activity": "Take a scenic drive to Mount Edith Cavell and hike to the Angel Glacier. Visit the Jasper Yellowhead Museum and learn about the history and culture of the area. Take a boat tour on Patricia Lake and enjoy the peacefulness of the water. In the evening, dine at a cozy restaurant and savor the flavors of the Canadian Rockies.",
                "date": "Dec 25, 2023",
                "special_attractions": "Experience dog sledding and enjoy the thrill of being pulled by a team of huskies through the snowy wilderness. Visit the Marmot Basin Ski Area and enjoy a day of skiing or snowboarding. Take a scenic drive to the Sunwapta Falls and witness the powerful cascades. Explore the stunning landscapes of the Tonquin Valley and hike to the Amethyst Lakes."
            },
            {
                "city": "Jasper (AB)",
                "activity": "Embark on a wildlife photography tour and capture stunning shots of animals in their natural habitat. Take a scenic drive to Medicine Lake and enjoy the peacefulness of the water. Visit the Jasper-Yellowhead Museum and learn about the history and culture of the area. In the evening, dine at a mountain lodge and enjoy a delicious meal featuring local ingredients.",
                "date": "Dec 26, 2023",
                "special_attractions": "Take a scenic hike to the Bald Hills and enjoy panoramic views of the surrounding mountains and valleys. Visit the Jasper Planetarium and learn about the wonders of the night sky. Take a horse-drawn sleigh ride through the snow-covered landscapes. Explore the stunning landscapes of the Maligne Valley and hike to the Maligne Canyon."
            }
        ]}

        sample_itinerary["error"] = str(e)
        i_response = sample_itinerary
    return Response(data=i_response, status=200)


def openai_generate_itinerary(data):
    OPENAI_KEY = settings.OPENAI_SECRET
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY
    chat_model = ChatOpenAI(
        temperature=1.0, model_name="gpt-3.5-turbo-16k")

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
    - You should include itinerary item for each day.
    - Your response should include JSON list of arrays with these keys: city (string), activity (string, 50-100 words), date (string), special_attractions (string, 50-100 words).
    Sample Response:
    {{
        "itinerary": [{{}}, {{}}, {{}},]
    }}
    """

    message = [SystemMessage(content=ITINERARY_PROMPT)]
    response = json.loads(chat_model.invoke(message).content)

    return response
