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

model_name = "gemini-1.5-flash"
#Choose a Gemini model.
model = genai.GenerativeModel(model_name=model_name)


def analyze_face(image_path):
    """
    Function to analyze facial features using xAI API
    """
    # Convert image to base64
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    base64_image = encode_image(image_path)
    
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
    - description: Object with "standout" and "weaknesses" arrays
    - image_quality: Object with quality assessment details

    Please ensure all numeric scores are provided as integers between 0 and 100.""" 

    response = model.generate_content([prompt, base64_image]
                                  , generation_config=genai.GenerationConfig(temperature=0.1, response_mime_type="application/json" ))
    
    # Parse JSON response
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {"error": "Failed to parse API response"}


