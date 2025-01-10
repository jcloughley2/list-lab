from django.conf import settings
import json
import requests
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ListGenerationService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info("ListGenerationService initialized")

    def generate_list(self, prompt: str) -> Dict:
        """
        Generate a list using OpenAI's API based on the user's prompt.
        Returns a dictionary containing the title and content.
        """
        logger.info(f"Generating list for prompt: {prompt}")
        
        system_prompt = """You are a helpful assistant that generates concise, simple lists based on user prompts.
        Your task is to create a list with the following rules:
        1. Generate no more than 10 items
        2. Keep each item very brief (max 10-15 words)
        3. Make items clear and straightforward
        4. No descriptions or explanations - just simple bullet points
        5. No numbering or special formatting - just plain text items
        
        Format your response as JSON with the following structure:
        {
            "title": "A brief, catchy title",
            "content": ["Item 1", "Item 2", "Item 3", ...]
        }
        
        Example response:
        {
            "title": "Essential Camping Gear",
            "content": [
                "Waterproof tent",
                "Sleeping bag rated for local climate",
                "Headlamp with extra batteries",
                "First aid kit",
                "Water filter or purification tablets"
            ]
        }"""

        try:
            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            
            logger.info("Making request to OpenAI API")
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            logger.info(f"OpenAI API response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.text}")
                raise Exception(f"OpenAI API error: {response.text}")
            
            result = response.json()
            logger.info("Successfully got JSON response from OpenAI")
            
            content = result['choices'][0]['message']['content']
            logger.info(f"Raw content from OpenAI: {content}")
            
            try:
                # Parse the JSON response
                parsed_content = json.loads(content)
                logger.info("Successfully parsed content as JSON")
                
                # Ensure all required fields are present
                required_fields = ['title', 'content']
                for field in required_fields:
                    if field not in parsed_content:
                        logger.error(f"Missing required field: {field}")
                        raise ValueError(f"Missing required field: {field}")
                
                # Ensure content is a list and has 10 or fewer items
                if not isinstance(parsed_content['content'], list):
                    parsed_content['content'] = parsed_content['content'].split('\n')
                parsed_content['content'] = parsed_content['content'][:10]
                
                logger.info("All validation passed, returning result")
                return parsed_content
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                raise Exception("Failed to parse OpenAI response as JSON")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"General error: {str(e)}")
            raise Exception(f"Failed to generate list: {str(e)}") 