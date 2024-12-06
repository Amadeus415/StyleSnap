
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    XAI_API_KEY = os.getenv('XAI_API_KEY')

    