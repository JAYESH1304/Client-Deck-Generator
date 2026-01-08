import google.generativeai as genai
import os
import random

# 1. Configure Gemini API
# Make sure to set your API key in the environment
# e.g. in terminal: export GEMINI_API_KEY="your_api_key"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 2. Prompt template for generating dummy user input
prompt_template = """
You are an AI assistant that generates dummy user inputs for testing.
The user input should include:
1. Industry name 
2. A problem statement related to AI in that industry
3. A user's approach to solve that problem using AI techniques

Return the result strictly in JSON format with keys:
- industry
- problem_statement
- user_approach
"""

# 3. Function to generate a new dummy input
def generate_dummy_input():
    # model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt_template)
    
    try:
        # Parse model response as JSON-like text
        text = response.text.strip()
        return text
    except Exception as e:
        return {"error": str(e), "raw_output": response.text}

if __name__ == "__main__":
    
    result = generate_dummy_input()
    print(result)
        