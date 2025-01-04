# RUMORS: Restful Utilities for Movies Online Recommender System

## Overview
RUMORS is a framework designed to implement RESTful APIs for a Recommender System using the MovieLens dataset.

## Features
- RESTful API for recommendations
- Scalable and upgradable architecture
- Utilizes collaborative filtering for movie recommendations

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/rumors.git
    cd rumors
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the application:
    ```sh
    python api/run.py
    ```

## Usage
### API Endpoints
- `POST /recommend`: Get movie recommendations for a user.

Example:
```json
{
  "user_id": 1
}
