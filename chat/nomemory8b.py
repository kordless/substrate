import os
import sys
import json
import asyncio
import logging
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import print_formatted_text
from coolname import generate_slug
from substrate import Substrate, Llama3Instruct70B, sb, Box, ComputeText, Llama3Instruct8B

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

CONFIG_DIR = os.path.expanduser('~/.config/llama3-chat')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

def load_or_create_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            logging.info(f"Config loaded from {CONFIG_FILE}")
            return config
        else:
            api_key = input("Please enter your Substrate API key: ")
            config = {'api_key': api_key}
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            logging.info(f"Config file created at {CONFIG_FILE}")
            return config
    except Exception as e:
        logging.error(f"Error loading or creating config: {str(e)}")
        return None

async def main():
    config = load_or_create_config()
    if not config:
        logging.error("Failed to load or create config. Exiting.")
        return

    api_key = config.get('api_key')
    if not api_key:
        logging.error("API key not found in config. Exiting.")
        return

    try:
        substrate = Substrate(api_key=api_key)
    except Exception as e:
        logging.error(f"Error initializing Substrate: {str(e)}")
        return

    bindings = KeyBindings()

    @bindings.add('c-c')
    def _(event):
        """ Pressing Ctrl+C will exit the application """
        event.app.exit()

    style = Style.from_dict({
        'username': '#ansigreen bold',
        'prompt': '#ansiblue',
        'llm-response': '#ansiyellow italic',
    })

    session = PromptSession(
        history=FileHistory(os.path.expanduser('~/.llama3-chat-history')),
        key_bindings=bindings,
        style=style
    )

    username = generate_slug(2)
    print_formatted_text(FormattedText([('class:username', f"Your generated username is: {username}")]), style=style)
    print_formatted_text(FormattedText([('class:llm-response', "Welcome to Llama3Instruct70B Chat! Type 'exit' or 'quit' to end the session.")]), style=style)

    while True:
        try:
            user_input = await session.prompt_async(
                FormattedText([
                    ('class:username', f'{username}'),
                    ('class:prompt', '> ')
                ])
            )
            if user_input.lower() in ['exit', 'quit', None]:
                print_formatted_text(FormattedText([('class:llm-response', 'Goodbye!')]), style=style)
                break
            
            print("setup query")
            llama3_query = Llama3Instruct8B(
                prompt=user_input,
                num_choices=2,
                temperature=0.4,
                max_tokens=800,
            )
            print("querying")
            try:
                response = substrate.run(llama3_query)
                print("got response")
                llm_response = response.get(llama3_query).choices[0].text
                print("printing response")
                print_formatted_text(FormattedText([('class:llm-response', f"Llama3: {llm_response.strip()}")]), style=style)
            except Exception as e:
                logging.error(f"Error querying Llama3Instruct70B: {str(e)}")
                print_formatted_text(FormattedText([('class:llm-response', "Sorry, I encountered an error. Please try again.")]), style=style)

        except EOFError:
            print_formatted_text(FormattedText([('class:llm-response', 'Goodbye!')]), style=style)
            break

if __name__ == '__main__':
    asyncio.run(main())