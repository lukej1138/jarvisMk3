FROM python:3.12.3-slim

RUN apt-get update && apt-get install -y curl ca-certificates procps && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh
WORKDIR /app

COPY ModelStorage/Modelfile ./
COPY ModelStorage/Classifier.py ./
COPY ModelStorage/ClassifierServer.py ./
COPY runOllama.sh ./

RUN python3 -m pip install --no-cache-dir flask ollama

EXPOSE 11434
EXPOSE 8080

RUN chmod +x /app/runOllama.sh

CMD ["bash", "/app/runOllama.sh"]