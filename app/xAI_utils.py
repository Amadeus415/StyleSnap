import os
from openai import OpenAI
import base64
from config import Config
import json


client = OpenAI(
    api_key=Config.XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)


def analyze_face(image_path):
    """
    Function to analyze facial features using xAI API
    """
    # Convert image to base64
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    base64_image = encode_image(image_path)
    
    # Prepare API message
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high",
                    },
                },
                {
                    "type": "text",
                    "text": """
                    You are an advanced facial analysis machine, 
                    
                    respond in the following format: 
                    {
                        "score": 0,
                        "pscore": 0, 
                        "masculinity": 0,
                        "skin": 0,
                        "jawline": 0,
                        "hair": 0,
                        "style": 0,
                        "smile": 0,
                        "visual_age": 0,
                        "description": "provide a description of their appearance and potential age",
                        "age_percentile": ex: Top 10%,
                        "image_quality": explain how good of a photo its is, if it is not a good photo explain how they could have choosen a better one.
                    }

                    Notes:
                    - The overall score is a number between 0 and 100, and it is the sum of all the other scores.
                    - Potential score should be what the person would rank if they improve on stats
                    - For the description, It is important to sell the customer on what they can do to improve their score, talk about they life benefits of having a higher score with dating and social life.
                    - Output must be in JSON format, with nothing preceding or following the JSON brackets
                    """,
                },
            ],
        },
    ]
    
    # Make API call
    stream = client.chat.completions.create(
        model="grok-vision-beta",
        messages=messages,
        stream=True,
        temperature=0.01,
    )
    
    # Collect response
    output = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            output += chunk.choices[0].delta.content
    
    # Parse JSON response
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {"error": "Failed to parse API response"}

