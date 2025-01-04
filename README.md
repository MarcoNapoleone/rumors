# RUMORS: Restful Utilities for Movies Online Recommender System

## Overview
RUMORS is a framework designed to implement RESTful APIs for a Recommender System using the MovieLens dataset. The system provides personalized movie recommendations based on user preferences and behavior.

## Features
- Movie recommendation engine with explanation capabilities
- User rating system and feedback collection
- RESTful API architecture
- Movie search and filtering
- User management with personality profiling (OCEAN scores)
- JWT-based authentication


## Running the Application

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
    python ./run.py
    ```
   The application will be running on `http://localhost:5000`.

### Docker
You can also run the application using Docker compose:
```sh
  docker compose up -d
```
The application will be running on `http://localhost:5000`.

## Example HTTP Requests

### 1. Create a New User

```http
POST /api/users/ HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
    "browser": "Chrome",
    "os": "Windows",
    "language": "en-US"
}
```

Response:
```json
{
    "user": {
        "test_group": "A",
        "email": "user@example.com",
        "age": 18,
        "browser": "Chrome",
        "os": "Windows",
        "language": "en-US"
    },
    "token": "<JWT_TOKEN>"
}
```

### 2. Get Movie Recommendations for a User

```http
GET /api/users/123/recommendations/ HTTP/1.1
Host: localhost:5000
Authorization: Bearer <JWT_TOKEN>
```

Response:
```json
[
    {
        "item_id": "tt0111161",
        "pred_score": 4.5,
        "is_known": false,
        "timestamp": "2024-01-04T10:30:00Z"
    },
    {
        "item_id": "tt0068646",
        "pred_score": 4.3,
        "is_known": false,
        "timestamp": "2024-01-04T10:30:00Z"
    }
]
```

### 3. Search Movies with Filtering

```http
GET /api/items/?query=matrix&sort=relevance&limit=2 HTTP/1.1
Host: localhost:5000
Authorization: Bearer <JWT_TOKEN>
```

Response:
```json
[
    {
        "title": "The Matrix",
        "genres": ["Action", "Sci-Fi"],
        "imdb_id": "tt0133093",
        "tmdb_id": "603"
    },
    {
        "title": "The Matrix Reloaded",
        "genres": ["Action", "Sci-Fi"],
        "imdb_id": "tt0234215",
        "tmdb_id": "604"
    }
]
```

## API Documentation
Full API documentation is available at `/api/docs` when running the application.

### Key Endpoints

- `/api/users/`: User management
- `/api/users/{id}/recommendations/`: User-specific recommendations
- `/api/users/{id}/ocean`: User personality profiling
- `/api/items/`: Movie search and browsing
- `/api/recommendations/{id}/explain`: Recommendation explanations

## Authentication
The API uses JWT (JSON Web Token) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## Error Handling
The API returns standard HTTP status codes:
- 200: Success
- 201: Resource created
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Resource not found
- 500: Internal server error


