import base64
import os
from google import genai
from google.genai import types
import json

def analyze_face(image_data):
    # Debug the input data
    print(f"Input image_data type: {type(image_data)}")
    print(f"Input image_data length: {len(image_data) if isinstance(image_data, bytes) else 'N/A'}")
    
    # Handle image data input
    if isinstance(image_data, str) and os.path.isfile(image_data):
        # If image_data is a file path
        with open(image_data, "rb") as image_file:
            image_bytes = image_file.read()
    elif isinstance(image_data, bytes):
        # If image_data is binary data
        image_bytes = image_data
    else:
        raise ValueError(f"Invalid image data format: {type(image_data)}")
    
    # Convert to base64 for debugging
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    print(f"Base64 image length: {len(base64_image)}")
    
    # Initialize the client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    print(f"API key first 5 chars: {api_key[:5]}...")
    
    client = genai.Client(api_key=api_key)
    
    # Define the model
    model = "gemini-2.0-flash"
    print(f"Using model: {model}")
    
    # Try a simpler approach - use the raw bytes directly
    try:
        contents = [
            types.Content(
                role="user",
                parts=[
                    # Use the raw bytes directly instead of base64 encoding/decoding
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/jpeg"
                    ),
                    types.Part.from_text(
                        text="""Please analyze this face and provide scores for the following attributes on a scale of 1-100: """
                    ),
                ],
            ),
        ]
        
        # Define the response schema
        generate_content_config = types.GenerateContentConfig(
        temperature=0.5,
        top_p=0.99,
        top_k=64,
        max_output_tokens=8192,
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            enum = [],
            required = ["score", "potential_score", "confidence", "skin", "jawline", "hair", "smile"],
            properties = {
                "score": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
                "potential_score": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
                "confidence": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
                "skin": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
                "jawline": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
                "hair": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
                "smile": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
            },
        ),
        system_instruction=[
            types.Part.from_text(
                text=""" You are a professional image analysis model. Analyze the provided images and output a structured JSON response with the following specific scores and attributes:

                Required fields:
                - score (0-100): Overall attractiveness score
                - potential_score (0-100): Potential score with improvements
                - confidence (0-100): Confidence in the analysis
                - skin (0-100): Skin quality score
                - jawline (0-100): Jawline definition score
                - hair (0-100): Hair quality and style score
                - smile (0-100): Smile quality score """
                        ),
                    ],
        )
        
        print("Sending request to Gemini API...")
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        print(f"Response received: {response}")
        
        # Process the response
        if response.candidates and response.candidates[0].content:
            text_response = response.candidates[0].content.parts[0].text
            print(f"Raw response text: {text_response}")
            
            # Try to parse as JSON
            try:
                result = json.loads(text_response)
            except json.JSONDecodeError:
                # If not valid JSON, create a structured response
                result = {
                    "score": 10,  # Default values
                    "potential_score": 85,
                    "confidence": 80,
                    "skin": 70,
                    "jawline": 75,
                    "hair": 80,
                    "smile": 75,
                    "raw_response": text_response  # Include the raw text
                }
            
            print(f"Final result: {json.dumps(result, indent=2)}")
            return result
        else:
            error_msg = {"error": "No response generated"}
            print(json.dumps(error_msg, indent=2))
            return error_msg
            
    except Exception as e:
        print(f"Error in analyze_face: {str(e)}")
        # Return a default response instead of raising an exception
        return {
            "score": 15,
            "potential_score": 80,
            "confidence": 75,
            "skin": 65,
            "jawline": 70,
            "hair": 75,
            "smile": 70,
            "error": str(e)
        }

# Example usage
# image_path = "D:/Projects/AI_Applications/prompt_engineering/facial_analysis/pic.jpg"
# with open(image_path, "rb") as image_file:
#     image_data = image_file.read()
# analyze_face(image_data)