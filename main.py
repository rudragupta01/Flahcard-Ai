import os
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env file
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Test API call
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": "Generate 2 flashcards about Python programming. Format each as Q: and A:"
        }
    ]
)

# Print the response
print(response.choices[0].message.content)