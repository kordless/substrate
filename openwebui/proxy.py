import os
import json
import logging
import time
from datetime import datetime
from quart import Quart, request, jsonify, Response
from quart.helpers import stream_with_context
from substrate import Substrate, ComputeText

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Quart(__name__)

CONFIG_DIR = os.path.expanduser('~/.config/substrate-chat')
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

config = load_or_create_config()
if not config:
    logging.error("Failed to load or create config. Exiting.")
    exit(1)

api_key = config.get('api_key')
if not api_key:
    logging.error("API key not found in config. Exiting.")
    exit(1)

substrate = Substrate(api_key=api_key, timeout=60 * 5)

# List of valid models with estimated parameter sizes and streaming support
valid_models = {
    "Mixtral8x7BInstruct": {"parameter_size": "56B", "stream": True},
    "Llama3Instruct70B": {"parameter_size": "70B", "stream": True},
    "Llama3Instruct8B": {"parameter_size": "8B", "stream": True},
    "Mistral7BInstruct": {"parameter_size": "7B", "stream": True},
    "Llama3Instruct405B": {"parameter_size": "405B", "stream": True},
    "gpt-4o": {"parameter_size": "200B", "stream": False},
    "gpt-4o-mini": {"parameter_size": "70B", "stream": False},
    "claude-3-5-sonnet-20240620": {"parameter_size": "2T", "stream": False}
}

@app.route('/api/chat', methods=['POST'])
async def chat():
    @stream_with_context
    async def sse_stream(query, model):
        logging.debug("Entering sse_stream generator")
        start_time = datetime.utcnow()
        try:
            response = await substrate.async_stream(query)
            logging.debug("Received response from substrate.async_stream")
        except Exception as e:
            logging.error(f"Error in substrate.async_stream: {str(e)}", exc_info=True)
            yield json.dumps({'error': 'Internal Server Error'}) + '\n'
            return

        accumulated_text = ""

        try:
            async for event in response.async_iter():
                logging.debug(f"Received event: {event}")
                
                if hasattr(event, 'data'):
                    event_data = event.data  # event.data is already a dictionary
                    logging.debug(f"Event data: {event_data}")

                    if event_data['object'] == 'node.delta':
                        text = event_data['data']['text']
                        accumulated_text += text
                        created_at = datetime.utcnow().isoformat() + 'Z'
                        sse_data = json.dumps({
                            'model': f'Substrate:{model}',
                            'created_at': created_at,
                            'message': {
                                'role': 'assistant',
                                'content': text
                            },
                            'done': False
                        })
                        logging.debug(f"Sending SSE data: {sse_data}")
                        yield f"{sse_data}\n"
                    elif event_data['object'] == 'graph.result':
                        # Final message
                        end_time = datetime.utcnow()
                        total_duration = (end_time - start_time).total_seconds() * 1e9  # Convert to nanoseconds
                        done_data = json.dumps({
                            'model': f'Substrate:{model}',
                            'created_at': end_time.isoformat() + 'Z',
                            'message': {
                                'role': 'assistant',
                                'content': ''  # Empty content for final message, as per Ollama format
                            },
                            'done_reason': 'stop',
                            'done': True,
                            'total_duration': int(total_duration),
                            'load_duration': 2986624900,  # Example value
                            'prompt_eval_count': 16,  # Example value
                            'prompt_eval_duration': 63076000,  # Example value
                            'eval_count': 341,  # Example value
                            'eval_duration': 10140732000  # Example value
                        })
                        logging.debug(f"Sending final SSE data: {done_data}")
                        yield f"{done_data}\n"
                else:
                    logging.warning(f"Received unexpected event: {event}")
        except Exception as e:
            logging.error(f"Error in sse_stream generator: {str(e)}", exc_info=True)
            yield json.dumps({'error': 'Stream processing error'}) + '\n'

        logging.debug("Exiting sse_stream generator")

    logging.debug("Entering chat endpoint")
    try:
        headers = request.headers
        raw_data = await request.data
        content_type = headers.get('Content-Type')

        logging.debug(f"Headers: {headers}")
        logging.debug(f"Content-Type: {content_type}")
        logging.debug(f"Raw Data: {raw_data}")

        if content_type != 'application/json':
            logging.debug("Content-Type is not application/json, attempting to parse raw data as JSON")
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                logging.error("Failed to parse raw data as JSON")
                return jsonify({'error': 'Invalid JSON'}), 400
        else:
            data = await request.get_json()

        logging.debug(f"Parsed JSON Data: {data}")

        if data is None:
            logging.error("Parsed data is None")
            return jsonify({'error': 'Invalid JSON'}), 400

        model = data.get('model', '').replace('Substrate:', '')
        messages = data.get('messages', [])
        temperature = data.get('temperature', 0.4)
        max_tokens = data.get('max_tokens', 800)
        stream = data.get('stream', True)

        logging.debug(f"Model: {model}, Temperature: {temperature}, Max Tokens: {max_tokens}, Stream: {stream}")

        if model not in valid_models:
            logging.error(f"Unsupported model: {model}")
            return jsonify({'error': 'Unsupported model'}), 400

        if not messages:
            logging.error("No messages provided")
            return jsonify({'error': 'No messages provided'}), 400

        # Check if streaming is supported for the model
        model_info = valid_models[model]
        supports_streaming = model_info['stream']

        # If streaming is requested but not supported, set stream to False
        if stream and not supports_streaming:
            logging.warning(f"Streaming not supported for model {model}. Falling back to non-streaming request.")
            stream = False

        # Concatenate messages into a single prompt
        prompt = '\n'.join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages if 'content' in msg])
        logging.debug(f"Generated prompt: {prompt}")

        # Initialize the appropriate model query
        query = ComputeText(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            num_choices=1,
            model=model
        )
        logging.debug(f"Created ComputeText query: {query}")

        if stream:
            logging.info("Starting streaming response")
            return Response(sse_stream(query, model), mimetype='application/x-ndjson')
        else:
            logging.info("Starting non-streaming response")
            return Response(non_streaming_response(query, model), mimetype='application/x-ndjson')

    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal Server Error'}), 500


async def non_streaming_response(query, model):
    try:
        start_time = time.time()
        response = await substrate.async_run(query)
        end_time = time.time()
        
        logging.debug(f"Raw response from Substrate API: {response}")
        
        if hasattr(response, 'api_response'):
            api_response = response.api_response
            logging.debug(f"API Response type: {type(api_response)}")
            logging.debug(f"API Response attributes: {dir(api_response)}")
            
            if hasattr(api_response, 'json') and isinstance(api_response.json, dict):
                content = api_response.json
                logging.debug(f"JSON content: {content}")
            else:
                logging.error(f"Unable to find JSON content in api_response: {api_response}")
                yield json.dumps({'error': 'No JSON content found in API response'}).encode('utf-8') + b'\n'
                return

            # Extract text from content
            if isinstance(content, dict):
                data = content.get('data', {})
                if data:
                    first_key = next(iter(data))
                    text = data[first_key].get('text')
                else:
                    text = None
            else:
                logging.error(f"Unexpected content type: {type(content)}")
                yield json.dumps({'error': 'Unexpected content type in API response'}).encode('utf-8') + b'\n'
                return

        if text is None:
            logging.error(f"No text content found in response: {content}")
            yield json.dumps({'error': 'No text content found in API response'}).encode('utf-8') + b'\n'
            return

        # Calculate durations
        total_duration = int((end_time - start_time) * 1e9)  # Convert to nanoseconds
        
        # Create Ollama-compatible response in chunks
        for i in range(0, len(text), 50):  # Chunk the response by 50 characters
            chunk = text[i:i + 50]
            result = {
                "model": f"Substrate:{model}",
                "created_at": datetime.utcnow().isoformat() + 'Z',
                "message": {
                    "role": "assistant",
                    "content": chunk
                },
                "done": False
            }
            yield json.dumps(result).encode('utf-8') + b'\n'

        # Send the final response
        final_result = {
            "model": f"Substrate:{model}",
            "created_at": datetime.utcnow().isoformat() + 'Z',
            "message": {
                "role": "assistant",
                "content": ""  # Final empty content
            },
            "done": True,
            "total_duration": total_duration,
            "load_duration": 0,
            "prompt_eval_count": 0,
            "prompt_eval_duration": 0,
            "eval_count": 0,
            "eval_duration": 0,
            "done_reason": "stop"
        }
        
        yield json.dumps(final_result).encode('utf-8') + b'\n'

    except Exception as e:
        logging.error(f"Error in non-streaming response: {str(e)}", exc_info=True)
        error_response = {
            "error": "Internal Server Error",
            "done": True
        }
        yield json.dumps(error_response).encode('utf-8') + b'\n'


    
@app.route('/api/tags', methods=['GET'])
async def list_local_models():
    try:
        models = [
            {
                "name": f"Substrate:{model}",
                "model": f"Substrate:{model}",
                "modified_at": datetime.utcnow().isoformat() + 'Z',
                "size": 4661226402,  # Example size, adjust accordingly
                "digest": f"{model}-digest",  # Unique digest
                "details": {
                    "parent_model": "",
                    "format": "gguf",
                    "family": "llama",
                    "families": ["llama"],
                    "parameter_size": info["parameter_size"],
                    "quantization_level": "Q4_0"
                }
            } for model, info in valid_models.items()
        ]
        return jsonify({"models": models})
    except Exception as e:
        logging.error(f"Error in list_local_models endpoint: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/api/version', methods=['GET'])
async def get_version():
    try:
        version_info = {
            "version": "0.3.0"
        }
        return jsonify(version_info)
    except Exception as e:
        logging.error(f"Error in get_version endpoint: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(port=11435)