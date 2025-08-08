import openai
from groq import Groq
import os
import json

from dotenv import load_dotenv

load_dotenv()

def generate_llm_response(messages, model_name, **kwargs):
    # Set default parameters
    max_tokens = kwargs.get('max_tokens', 1000)
    temperature = kwargs.get('temperature', 0.7)
    top_p = kwargs.get('top_p', 1.0)

    api_key = kwargs.get('api_key', "")
    
    if model_name == "deepseek":
        model_name = "deepseek-r1-distill-llama-70b"
    elif model_name == "llama":
        model_name = "meta-llama/llama-4-maverick-17b-128e-instruct"
    
    try:
        # Route to OpenAI if model contains 'gpt'
        if 'gpt' in model_name.lower():
            if not api_key:
                api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for GPT models")
            
            client = openai.OpenAI(api_key=api_key)
        
        # Route to Groq for all other models
        else:
            if not api_key:
                api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is required for non-GPT models")
            
            client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            response_format={ "type": "json_object" },
            temperature=temperature,
            top_p=top_p,
        )
         
        return response.choices[0].message.content
            
    except Exception as e:
        raise ValueError(f"Failed to generate response: {str(e)}")
