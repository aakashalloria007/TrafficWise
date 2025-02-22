import ollama
from flask import Flask
from ollama import chat
from flask_mysqldb import MySQL
import mysql.connector



# Initialize chat with Navision specific formatting
messages = [
    {
        'role': 'system',
        'content': '''<｜begin▁of▁sentence｜>You are Navision, an AI assistant and only answer to prompts related to travel, navigation, traffic, and similar topics. 
        You operate in a helpful, honest, and harmless manner.'''
    }
]

# Navision recommended parameters
params = {
        'temperature': 0.7,  # Controls randomness (0.1-1.0)
        'top_p': 0.9,  # Nucleus sampling threshold
        'top_k': 40,  # Limit to top K tokens
        'max_tokens': 512,  # Maximum response length
        'repeat_penalty': 1.1,  # Reduce repetition
        'stream': True  # Enable streaming mode if supported
}

print("Hello! I'm Navision, your AI assistant. How can I help you today?")

while True:
    try:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Navision: Goodbye! Have a great day!")
            break

        # Add user message with DeepSeek formatting
        messages.append({
            'role': 'user',
            'content': f'{user_input}'
        })
        # Initialize a streaming response
        print("Navision: ", end='', flush=True)

        stream = chat(
            model='deepseek-r1:1.5b',
            messages=messages,
            options=params,
            stream= True  # Enable streaming mode if supported
        )

        bot_response = ""
        for chunk in stream:
            bot_response += chunk['message']['content']
            print(chunk['message']['content'], end='', flush=True)


        print()  # End the current response with a newline

        # Add formatted assistant response to message history
        messages.append({
            'role': 'assistant',
            'content': f'<｜assistant▁answer｜>{bot_response}<｜end▁of▁sentence｜>'
        })

    except KeyboardInterrupt:
        print("\nNavision: Session ended. Feel free to return anytime!")
        break
