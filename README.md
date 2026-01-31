## Personal AI Assistant (JARVIS MARK 3!)

Hello! This has been the project I've worked on the longest and am the most passionate about. Jarvis was inspired by, well, the actual Jarvis AI assistant to Tony Stark in the _Avengers_ Movie. Though this rendition of Jarvis is significantly smaller, I've attempted to incorporate many elements I would imagine the real thing would have.

###

### Notable Features:

- Speech Recognition using a Google Speech Recognition Library
- Text To Speech via KokoroTTS 80M, a lightweight text-to-speech generator with 20+ voices and only 80 million parameters
- Prompt categorization using the Ollama 7.2b LLM (Now Fully Containerized!)
- Spotify and Calendar Management capabilities
- Calculator/WolframAlpha features
- Browser interaction

### 

### Quickstart:

**Note:** You must provide your own Spotify, WolframAlpha, and Google API credentials to run this project

Start by cloning this repository locally; from there, create a local virtual environment and install the required dependencies using either the uv.lock and `uv sync` or `pip install -r requirements.txt`. From their, edit the `.env-template` to include your API credentials; make sure to change the file name to `.env` only. Finally, run `docker compose up -d` to start the LLM for categorization, and run the driver file AI.py.
