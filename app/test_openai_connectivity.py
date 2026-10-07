"""Minimal terminal chat app for OpenAI.

Setup:
    pip install openai
    export OPENAI_API_KEY="your-key-here"   # Windows: setx OPENAI_API_KEY "your-key-here"

Run:
    python chat.py
"""

from openai import OpenAI

MODEL = "gpt-4o-mini"  # swap for any chat model your account has access to
SYSTEM_PROMPT = "You are a helpful assistant."

client = OpenAI()  # reads OPENAI_API_KEY from the environment


def main():
    # The full history is sent each turn so the model has conversation context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Chat started. Type 'quit' or 'exit' to leave.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        # Stream the reply so text appears as it's generated
        print("AI: ", end="", flush=True)
        reply = ""
        stream = client.chat.completions.create(
            model=MODEL, messages=messages, stream=True
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            reply += delta
        print("\n")

        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
