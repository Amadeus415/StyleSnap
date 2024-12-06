# functions
import json
import os

def load_amazon_products():
    """Load Amazon products from JSON file"""
    json_path = os.path.join(os.path.dirname(__file__), 'data', 'amazon_products.json')
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
            return data.get('products', [])
    except Exception as e:
        print(f"Error loading products: {e}")
        return []