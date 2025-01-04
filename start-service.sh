#!/bin/bash

# Load environment variables from the .env file in the current directory
ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
    # Load the .env file using source
    source "$ENV_FILE"
fi

if [ -z "$OPENROUTER_KEY" ]; then
    echo "OpenRouter key not found. Starting all services, including Ollama, to download the model..."

    if [ "$LLM_ENDPOINT_TYPE" = "ollama" ]; then
        echo "LLM_ENDPOINT_TYPE is 'ollama'. Starting Ollama..."
        docker-compose --profile ollama up
    else
        echo "LLM_ENDPOINT_TYPE is 'openrouter' or invalid. Starting all services, including Ollama."
        docker-compose up
    fi
else
    echo "OpenRouter key found."

    # Check if LLM_ENDPOINT_TYPE is either 'openrouter' or 'ollama'
    if [ "$LLM_ENDPOINT_TYPE" = "openrouter" ]; then
        echo "LLM_ENDPOINT_TYPE is 'openrouter'. Starting all services except Ollama."
        docker-compose up
    elif [ "$LLM_ENDPOINT_TYPE" = "ollama" ]; then
        echo "LLM_ENDPOINT_TYPE is 'ollama'. Starting all services, including Ollama."
        docker-compose --profile ollama up
    else
        echo "LLM_ENDPOINT_TYPE is empty or invalid. Starting all services without Ollama."
        docker-compose up
    fi
fi
