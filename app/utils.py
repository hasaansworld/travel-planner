import traceback
from openai import AsyncOpenAI
from groq import AsyncGroq
import os
import json

from dotenv import load_dotenv

load_dotenv()

async def generate_llm_response(messages, model_name, api_key="", **kwargs):
    # Set default parameters
    max_tokens = kwargs.get('max_tokens', 1000)
    temperature = kwargs.get('temperature', 0.7)
    top_p = kwargs.get('top_p', 1.0)
    # Get call stack info
    stack = traceback.extract_stack()
    caller = stack[-2]  # The function that called this one
    
    print(f"\n=== generate_llm_response DEBUG ===")
    print(f"Called from: {caller.filename}:{caller.lineno}")
    print(f"Called from function: {caller.name}")
    print(f"Call line: {caller.line}")
    print(f"api_key type: {type(api_key)}")
    print(f"api_key value: {repr(api_key)}")
    print(f"api_key bool: {bool(api_key)}")
    print(f"api_key length: {len(str(api_key))}")
    
    # Check if it's a Pydantic field
    if hasattr(api_key, 'annotation'):
        print(f"⚠️  API key is a Pydantic field!")
        print(f"Field default: {getattr(api_key, 'default', 'NO_DEFAULT')}")
        print(f"Field annotation: {getattr(api_key, 'annotation', 'NO_ANNOTATION')}")
    
    # Check kwargs for any api_key
    if 'api_key' in kwargs:
        print(f"⚠️  DUPLICATE: api_key also in kwargs: {repr(kwargs['api_key'])}")
    
    
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
            
            client = AsyncOpenAI(api_key=api_key)
        
        # Route to Groq for all other models
        else:
            if not api_key:
                api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is required for non-GPT models")
            
            client = AsyncGroq(api_key=api_key)

        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            response_format={ "type": "json_object" },
            temperature=temperature,
            top_p=top_p,
        )
         
        return response.choices[0].message.content
            
    except Exception as e:
        raise ValueError(f"Failed to generate response: {str(e)}")
