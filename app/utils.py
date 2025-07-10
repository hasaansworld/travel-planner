import openai
from groq import Groq
import os
import json

from dotenv import load_dotenv

load_dotenv()

def generate_llm_response(messages, model_name, function_schema, **kwargs):
    # Set default parameters
    max_tokens = kwargs.get('max_tokens', 1000)
    temperature = kwargs.get('temperature', 0.7)
    top_p = kwargs.get('top_p', 1.0)
    
    try:
        # Route to OpenAI if model contains 'gpt'
        if 'gpt' in model_name.lower():
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for GPT models")
            
            client = openai.OpenAI(api_key=api_key)
        
        # Route to Groq for all other models
        else:
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is required for non-GPT models")
            
            client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            functions=[function_schema],
            function_call="auto"
        )
        
        message = response.choices[0].message
            
        # Check if it's a function call
        if message.function_call:
            return {
                "function_call": {
                    "name": message.function_call.name,
                    "arguments": json.loads(message.function_call.arguments)
                }
            }
        else:
            return message.content
            
    except Exception as e:
        raise ValueError(f"Failed to generate response: {str(e)}")
