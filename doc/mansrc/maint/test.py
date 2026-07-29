from openai import OpenAI

# Configure the client for your custom provider
client = OpenAI(
    base_url="http://localhost:8000/v1",  # Replace with your provider's endpoint
    api_key="your-custom-provider-key"    # Use "none" if no key is required
)

response = client.chat.completions.create(
    model="your-custom-model-name",       # Specify the target provider model
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)