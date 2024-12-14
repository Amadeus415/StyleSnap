# Prompt Engineering

## To DO
 - [ ] For Description change it to bullet points structure
 - [ ]
 - [ ] 

## Prompt Improvement - What do I need to improve
1. Score need to be higher on average, and don't base score off image quality
2. Change description to bullet points structure
3. Change image_qaulity to bp structure around these metrics( Lighting, etc...)

{
                    "type": "text",
                    "text": """
                    You are an advanced facial analysis machine, 
                    
                    respond in the following format: 
                    {
                        "score": 0,
                        "pscore": 0, 
                        "confidence": 0,
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
                    - The overall score(score) is a number between 0 and 100, and it is the sum of all the other scores.
                    - Potential score(pscore) should be what the person would rank if they improve on stats
                    - For the description, list facts about how t
                    - Output must be in JSON format, with nothing preceding or following the JSON brackets
                    """,
                }


# Value
1. FaceMax: get score, and potential score
2. Dating Market Analysis - sex appeal, photo rating

# Potential things to add into AI analysis
1. Dating Market Appeal - Tinder Rating