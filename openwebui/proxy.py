import os
import json
import logging
from datetime import datetime
from quart import Quart, request, jsonify, Response
from quart.helpers import stream_with_context
from substrate import Substrate, ComputeText, MultiComputeText

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

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

# List of valid models with estimated parameter sizes
valid_models = {
    "Mixtral8x7BInstruct": "56B",  # 8 x 7B
    "Llama3Instruct70B": "70B",
    "Llama3Instruct8B": "8B",
    "Mistral7BInstruct": "7B",
    "Llama3Instruct405B": "405B"
}

@app.route('/api/chat', methods=['POST'])
async def chat():
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
                return jsonify({'error': 'Invalid JSON'}), 400
        else:
            data = await request.get_json()

        logging.debug(f"Parsed JSON Data: {data}")

        if data is None:
            return jsonify({'error': 'Invalid JSON'}), 400

        model = data.get('model', '').replace('Substrate:', '')
        messages = data.get('messages', [])
        temperature = data.get('temperature', 0.4)
        max_tokens = data.get('max_tokens', 800)
        stream = data.get('stream', True)

        if model not in valid_models:
            return jsonify({'error': 'Unsupported model'}), 400

        if not messages:
            return jsonify({'error': 'No messages provided'}), 400

        # Concatenate messages into a single prompt
        prompt = '\n'.join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages if 'content' in msg])

        # Initialize the appropriate model query
        query = MultiComputeText(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            num_choices=1,
            model=model
        )

        @stream_with_context
        async def sse_stream():
            start_time = datetime.utcnow()
            response = await substrate.async_stream(query)
            has_yielded = False
            accumulated_text = ""

            async for event in response.async_iter():
                event_data = event.data  # Already a dictionary

                if event_data['object'] == 'node.delta':
                    text = event_data['data']['choices']['item']['text']
                elif event_data['object'] == 'graph.result':
                    # Assuming the model name is the first key in the 'data' dict
                    model_key = next(iter(event_data['data']))
                    text = event_data['data'][model_key]['choices'][0]['text']
                else:
                    continue  # Skip unknown object types

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
                yield f"{sse_data}\n\n"
                has_yielded = True

            # Check if we haven't yielded anything yet but have accumulated text
            if not has_yielded and accumulated_text:
                created_at = datetime.utcnow().isoformat() + 'Z'
                sse_data = json.dumps({
                    'model': f'Substrate:{model}',
                    'created_at': created_at,
                    'message': {
                        'role': 'assistant',
                        'content': accumulated_text
                    },
                    'done': False
                })
                yield f"{sse_data}\n\n"

            # Final done message with additional data
            end_time = datetime.utcnow()
            total_duration = (end_time - start_time).total_seconds() * 1e9  # Convert to nanoseconds
            done_data = json.dumps({
                'model': f'Substrate:{model}',
                'created_at': end_time.isoformat() + 'Z',
                'message': {
                    'role': 'assistant',
                    'content': ''
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
            yield f"{done_data}\n\n"

        if stream:
            return Response(sse_stream(), mimetype='text/event-stream')
        else:
            # Handle non-streaming case (if needed)
            # This is a placeholder and should be implemented based on your requirements
            return jsonify({'error': 'Non-streaming requests are not implemented'}), 501

    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

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
                    "parameter_size": parameter_size,
                    "quantization_level": "Q4_0"
                }
            } for model, parameter_size in valid_models.items()
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
