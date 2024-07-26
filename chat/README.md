# Chat Application

This directory contains a Python chat application using the Substrate API.

## Getting Started

To begin using this project, you'll need to obtain an API key from Substrate. Follow these steps to get started:

1. **Visit the Substrate API**: Navigate to the following URL to retrieve your API key:
   - [https://substrate.run](https://substrate.run)
1. **Clone the repo:** `git clone <repo_url>`
1. **Navigate to the directory:** `cd chat`
1. **Install the required dependencies:** `pip install -r requirements.txt`
1. **Run the application:** `python memory70B.py` or `python nomemory8b.py`
1. **Input Your API Key:** Once you have your API key, you can input it into the application during startup when prompted.

## Application Overview

### memory70B.py

This script initializes and runs a chat session using the Llama3Instruct70B model. It includes functionalities like loading a configuration file, generating unique usernames, handling user input, and querying the Llama3 model.

#### Vector Store

This application uses a vector store to efficiently manage and query vector representations of data. This functionality enhances the capabilities of the chat application by allowing it to perform rapid similarity searches and other vector-based operations.

### nomemory8b.py

This script is similar to `memory70B.py` but uses the Llama3Instruct8B model instead. It also includes functionalities like loading a configuration file, generating unique usernames, handling user input, and querying the Llama3 model.

## Example Usage

An example chat session:

```
Your generated username is: portable-monkey
Welcome to Llama3Instruct70B Chat! Type 'exit' or 'quit' to end the session.
portable-monkey> my parrot is blue
Llama3: That's interesting! You've mentioned that your parrot is blue twice. Are you trying to emphasize the color of your parrot or is there something else you'd like to talk about regarding your feathered friend?
portable-monkey> what did i say before?
Llama3: You said "my parrot is blue"
portable-monkey> was there an emergency?
Llama3: No, there was no emergency. We were just having a conversation about your parrot. You mentioned that it's blue, and I responded with a question.
portable-monkey> write some python code to do fib sequence
Llama3: Sure! Here is a simple Python function that generates the Fibonacci sequence up to the nth number:
def fibonacci(n):
    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence
```
