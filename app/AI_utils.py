import os
from openai import OpenAI
import base64
from config import Config
import typing_extensions as typing
from typing import Dict, List
import json
import google.generativeai as genai

GEMINI_API_KEY = Config.GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

#Define the JSON schema
class Output(typing.TypedDict):
    score: int
    potential_score: int
    confidence: int
    skin: int
    jawline: int
    hair: int
    smile: int
    visual_age: int
    age_percentage: str
    description: Dict[str, List[str]]
    image_quality: Dict[str, typing.Union[str, List[str]]]
    recommendation: Dict[str, List[str]]
    lookalike: Dict[str, List[str]]

model_name = "gemini-1.5-flash"
#Choose a Gemini model.
model = genai.GenerativeModel(model_name=model_name)


def analyze_face(image_data):
    """
    Function to analyze facial features using xAI API
    image_data can be either a file path (str) or binary data (bytes)
    """
    # Convert image to base64
    if isinstance(image_data, str) and os.path.isfile(image_data):
        # If image_data is a file path
        with open(image_data, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    elif isinstance(image_data, bytes):
        # If image_data is binary data
        base64_image = base64.b64encode(image_data).decode("utf-8")
    else:
        raise ValueError("Invalid image data format")
    
    model_name = "gemini-1.5-flash"
    #Choose a Gemini model.
    model = genai.GenerativeModel(model_name=model_name)

    # Define the prompt
    prompt = """You are a professional image analysis model. Analyze the provided images and output a structured JSON response with the following specific scores and attributes:

    Required fields:
    - score (0-100): Overall attractiveness score
    - potential_score (0-100): Potential score with improvements
    - confidence (0-100): Confidence in the analysis
    - skin (0-100): Skin quality score
    - jawline (0-100): Jawline definition score
    - hair (0-100): Hair quality and style score
    - smile (0-100): Smile quality score
    - visual_age: Estimated age in years
    - age_percentage: Percentile ranking (e.g. "Top 15%")
    - description: Object with "standout", "weaknesses", "Life Benefits" arrays
    - image_quality: Object with quality assessment details

    - recommendation: Write a call to action for the user, that is tailored to their insecurities, making them want to see how to improve to potential_score. Make this brutal and honest. Explain to them the percent of the poptulation that they could be in. Really sell it, and make it sound like it is in thier reach but play on their insecurities.

    - lookalike: List of celebrity lookalikes that are similar to the user.

    Please ensure all numeric scores are provided as integers between 0 and 100."""

    response = model.generate_content([prompt, base64_image]
                                  , generation_config=genai.GenerationConfig(temperature=0.1, response_mime_type="application/json" ))
    
    # Parse JSON response
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse API response"}


