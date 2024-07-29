import os
import sys
import json
import asyncio
import logging
import time
import hashlib
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import print_formatted_text
from coolname import generate_slug
from substrate import Substrate, Llama3Instruct70B, FindOrCreateVectorStore, EmbedText, QueryVectorStore, DeleteVectorStore, sb, Box

# Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

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

def generate_time_hash():
    current_time = str(time.time())
    hash_object = hashlib.md5(current_time.encode())
    return f"{current_time}_{hash_object.hexdigest()[:10]}"

import ast

def extract_key_terms(text, llm_client, attempt=1, max_attempts=3):
    if attempt > max_attempts:
        logging.error(f"Failed to extract key terms after {max_attempts} attempts.")
        return []
    
    if attempt == 1:
        prompt = f"""Extract key terms from the following text and return them as a Python list.
Enclose the list in triple backticks (```) and set it equal to keyterms=.

Text: {text}

Key terms (format example):
```
keyterms = ["term1", "term2", "term3"]
```
"""
    else:
        prompt = f"""Your previous response was not in the correct format. Please provide a Python list of key terms extracted from the following text. Enclose the list in triple backticks (```) and set it equal to keyterms=.

Text: {text}

Correct format example:
```
keyterms = ["term1", "term2", "term3"]
```
"""

    llama3_query = Llama3Instruct70B(
        prompt=prompt,
        num_choices=1,
        temperature=0.2,
        max_tokens=200,
    )
    response = llm_client.run(llama3_query)
    llm_response = response.get(llama3_query).choices[0].text.strip()
    
    # Try to extract the list from between triple backticks
    start = llm_response.find('```')
    end = llm_response.rfind('```')
    if start != -1 and end != -1:
        code_block = llm_response[start+3:end].strip()
        try:
            # Execute the code block to get the keyterms
            local_vars = {}
            exec(code_block, {}, local_vars)
            if 'keyterms' in local_vars and isinstance(local_vars['keyterms'], list):
                return local_vars['keyterms']
        except Exception as e:
            logging.error(f"Failed to execute code block: {code_block}. Error: {str(e)}")
    
    # If we couldn't extract a list, try to parse the whole response
    try:
        key_terms = ast.literal_eval(llm_response)
        if isinstance(key_terms, list):
            return key_terms
    except Exception as e:
        logging.error(f"Failed to parse full response as list: {llm_response}. Error: {str(e)}")
    
    # If we still don't have a valid list, recurse
    return extract_key_terms(text, llm_client, attempt + 1, max_attempts)


class VectorStore:
    def __init__(self, substrate):
        self.substrate = substrate
        self.collection_name = generate_slug(2)
        self.embedding_model = "jina-v2"

    def initialize(self):
        # Delete existing vector store if it exists
        print(f"Initialized vector store: {self.collection_name}")

        # TODO list different collections and then manage
        """
        delete = DeleteVectorStore(
            collection_name=self.collection_name,
            model=self.embedding_model,
        )
        self.substrate.run(delete)
        """

        # Create a new vector store
        create = FindOrCreateVectorStore(
            collection_name=self.collection_name,
            model=self.embedding_model,
        )
        self.substrate.run(create)

    def add_entry(self, role, content, key_terms):
        time_hash = generate_time_hash()
        embed = EmbedText(
            text=f"{role}: {content}",
            collection_name=self.collection_name,
            model=self.embedding_model,
            metadata={
                "role": role,
                "time_hash": time_hash,
                "timestamp": time.time(),
                "key_terms": json.dumps(key_terms)
            }
        )
        self.substrate.run(embed)

    def get_recent_history(self, query_terms, limit=50):
        query = QueryVectorStore(
            query_strings=[" ".join(query_terms)] if query_terms else [""],
            collection_name=self.collection_name,
            model=self.embedding_model,
            include_metadata=True,
            top_k=limit,
        )
        query_res = self.substrate.run(query)
        query_out = query_res.get(query)
        
        history = []
        for result in query_out.results[0]:
            metadata = result.metadata
            role = metadata.get('role', 'Unknown')
            content = metadata.get('doc', '').split(': ', 1)[-1] if ': ' in metadata.get('doc', '') else metadata.get('doc', '')
            timestamp = metadata.get('timestamp', 0)
            key_terms = json.loads(metadata.get('key_terms', '[]'))
            history.append((timestamp, role, content, tuple(key_terms)))
        
        # Sort history by timestamp in ascending order
        history.sort(key=lambda x: x[0])
        
        # Extract key terms from top 10 results
        top_10_key_terms = set()
        for _, _, _, terms in history[:10]:
            top_10_key_terms.update(terms)
        
        # Perform second query with combined key terms
        combined_terms = list(set(query_terms) | top_10_key_terms)
        second_query = QueryVectorStore(
            query_strings=[" ".join(combined_terms)],
            collection_name=self.collection_name,
            model=self.embedding_model,
            include_metadata=True,
            top_k=limit,
        )
        second_query_res = self.substrate.run(second_query)
        second_query_out = second_query_res.get(second_query)
        
        # Combine results
        for result in second_query_out.results[0]:
            metadata = result.metadata
            role = metadata.get('role', 'Unknown')
            content = metadata.get('doc', '').split(': ', 1)[-1] if ': ' in metadata.get('doc', '') else metadata.get('doc', '')
            timestamp = metadata.get('timestamp', 0)
            key_terms = json.loads(metadata.get('key_terms', '[]'))
            history.append((timestamp, role, content, tuple(key_terms)))  # Convert key_terms list to tuple
        
        # Remove duplicates while preserving order
        seen = set()
        unique_history = []
        for item in history:
            item_hash = hash((item[0], item[1], item[2]))  # Hash based on timestamp, role, and content
            if item_hash not in seen:
                seen.add(item_hash)
                unique_history.append(item)
        
        # Sort unique history by timestamp
        unique_history.sort(key=lambda x: x[0])
        
        # Remove timestamp and key_terms from the final output
        return [(role, content) for _, role, content, _ in unique_history]

def process_user_input(text, llm_client, vector_store):
    key_terms = extract_key_terms(text, llm_client)
    vector_store.add_entry("Human", text, key_terms)
    return key_terms

def process_llm_response(text, llm_client, vector_store):
    key_terms = extract_key_terms(text, llm_client)
    vector_store.add_entry("Assistant", text, key_terms)
    return key_terms

def build_context(recent_history):
    return "\n".join([f"{role}: {content}" for role, content in recent_history])

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
        vector_store = VectorStore(substrate)
        vector_store.initialize()
        logging.info("Vector store initialized and reset.")
    except Exception as e:
        logging.error(f"Error initializing Substrate or Vector Store: {str(e)}")
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

            key_terms = process_user_input(user_input, substrate, vector_store)
            recent_history = vector_store.get_recent_history(key_terms)
            context = build_context(recent_history)

            llama3_query = Llama3Instruct70B(
                prompt=f"{context}\n\nAssistant:",
                num_choices=1,
                temperature=0.4,
                max_tokens=800,
            )

            try:
                response = substrate.run(llama3_query)
                llm_response = response.get(llama3_query).choices[0].text
                print_formatted_text(FormattedText([('class:llm-response', f"Llama3: {llm_response.strip()}")]), style=style)
                process_llm_response(llm_response.strip(), substrate, vector_store)
            except Exception as e:
                logging.error(f"Error querying Llama3Instruct70B: {str(e)}")
                print_formatted_text(FormattedText([('class:llm-response', "Sorry, I encountered an error. Please try again.")]), style=style)

        except EOFError:
            print_formatted_text(FormattedText([('class:llm-response', 'Goodbye!')]), style=style)
            break

if __name__ == '__main__':
    asyncio.run(main())