import os
from fastmcp.client import Client
import openai


# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_llm_with_context(query, context):
    messages = [
        {"role": "system", "content": "You are an assistant that uses external context."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message["content"]

def main():
    client = Client("http://127.0.0.1:5000")
    query = "What is this about?"

    # Ask the server for context
    response = client.ask("echo", query)
    context = response.get("context", "")

    # Ask OpenAI using the context
    answer = ask_llm_with_context(query, context)
    print("Answer:", answer)

if __name__ == "__main__":
    main()
