#!/bin/bash

# Verifica se MODEL_NAME è stato impostato
if [ -z "$MODEL_NAME" ]; then
    echo "MODEL_NAME is not set."
    exit 1
fi

# Start Ollama in the background.
/bin/ollama serve &
pid=$!
if [ $? -ne 0 ]; then
    echo "Failed to start Ollama."
    exit 1
fi

# Wait for Ollama to start by checking if it's running
while ! ollama list &> /dev/null; do
    echo "Waiting for Ollama to start..."
    sleep 1
done

# Verifica se il modello specificato è presente
if ! ollama list | grep -q "$MODEL_NAME"; then
    echo "Cloning $MODEL_NAME model..."
    ollama pull "$MODEL_NAME"
    if [ $? -ne 0 ]; then
        echo "Failed to pull $MODEL_NAME model."
        exit 1
    fi
    echo "---Done!---"
fi

# Wait for Ollama process to finish.
wait $pid

