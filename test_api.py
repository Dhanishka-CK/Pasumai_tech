from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    # List available models
    models = client.models.list()
    print("✅ Available models:")
    for model in models:
        print(f"  - {model.name}")
    
    # Test generation
    print("\n🧪 Testing generation...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Say hello in Tamil"
    )
    print(f"✅ Response: {response.text}")
    
except Exception as e:
    print(f"❌ Error: {e}")