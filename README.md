# Homelab API

This project is a simple FastAPI application designed to be deployed to a homelab environment using Jenkins and Docker. 

## Project Structure

```
/
├── docker-compose.yml
├── Dockerfile
├── Jenkinsfile
├── pyproject.toml
├── README.md
├── src/
│   ├── main.py
│   ├── api/v1/endpoints.py
│   ├── core/config.py
│   ├── db/session.py
│   ├── models/schemas.py
│   └── services/item_service.py
└── tests/
    ├── test_endpoints.py
    └── test_services.py
```

## Getting Started

### Prerequisites

*   Python 3.12+
*   uv
*   Docker

### Installation

1.  Clone the repository.
2.  Install the dependencies:

    ```bash
    uv pip install '.[dev]'
    ```

### Running the Application

```bash
uvicorn src.main:app --reload
```


The application will be available at `http://127.0.0.1:8000`.

### Running Tests

```bash
pytest
```

### Building with Docker

```bash
docker compose up --build
```
