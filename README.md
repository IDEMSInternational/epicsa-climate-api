# EPICSA Climate Api

API for accessing e-picsa climate services

Build with [FastAPI](https://fastapi.tiangolo.com/)

## Pre-Requisites

The documentation requires python 3.10+ to be installed:  
[https://www.python.org/downloads/](https://www.python.org/downloads/)

## Installation

Create an environment file from the sample. These will be populated using [Pydantic](https://docs.pydantic.dev/usage/settings/)

```
cp .env.sample .env
```

The scripts below will create a python [virtual environment](https://docs.python.org/3/library/venv.html), activate, install required dependencies and start local server

=== "Windows (powershell)"

    ``` ps1 linenums="1"
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```

=== "Linux (bash)"

    ```sh linenums="1"
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```

## Running locally

Once installed, subsequent server starts can skip installation steps

=== "Windows (powershell)"

    ``` ps1 linenums="1"
    .\.venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload
    ```

=== "Linux (bash)"

    ```sh linenums="1"
    source .venv/bin/activate
    uvicorn app.main:app --reload
    ```

The server will start at [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Running Tests

```py
pytest
```

## License

This project is licensed under the terms of the MIT license.
