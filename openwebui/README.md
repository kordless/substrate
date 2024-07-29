# Substrate Proxy for Open WebUI

This directory contains a Python proxy application designed to allow the use of Substrate through Open WebUI. This is an early, hacky implementation.

## Getting Started

To begin using this project, you'll need to obtain an API key from Substrate and have Docker Desktop installed and running. Follow these steps to get started:

1. **Visit the Substrate API**: Navigate to the following URL to retrieve your API key:
   - [https://substrate.run](https://substrate.run)
2. **Clone the repo:** `git clone <repo_url>`
3. **Navigate to the directory:** `cd openwebui`
4. **Install the required dependencies:** `pip install -r requirements.txt`

### Running the Application

1. **Run the proxy application:**
   ```sh
   python proxy.py
   ```
2. **Input Your API Key:** Once you have your API key for Substrate, you can input it into the application during startup when prompted.

### Running Open WebUI Docker Container

To run the Open WebUI Docker container, execute one of the following commands depending on your GPU availability:

- **With GPU Support:**
  ```sh
  docker run -d -p 3000:8080 --gpus all --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:cuda
  ```

- **Without GPU Support:**
  ```sh
  docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
  ```

You will need to navigate to the URL by clicking on it in Docker. To add the proxy to Open WebUI, go to your profile, click on `settings` then `admin settings`. Go to `connections` and then set the Ollama API to:

```
http://host.docker.internal:11435
```

Click the refresh button to the far right to load the models, which are proxied (not downloaded locally). 

Click on New Chat to select a model and chat with it.

## Video Tutorial

For a detailed walkthrough of setting up and using the Substrate Proxy for Open WebUI, check out our tutorial video:

[![Substrate Proxy for Open WebUI Tutorial](https://img.youtube.com/vi/JptVk1Aej64/0.jpg)](https://www.youtube.com/watch?v=JptVk1Aej64)

[Watch the Tutorial Video](https://www.youtube.com/watch?v=JptVk1Aej64)

## Notes

- This project is in its early stages and may contain bugs or unfinished features.
- Make sure Docker Desktop is installed and running on your machine before attempting to run the provided Docker commands.
