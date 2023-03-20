# EPICSA Climate Api

API for accessing e-picsa climate services

Build with [FastAPI](https://fastapi.tiangolo.com/)

## Pre-Requisites

The api requires python and R runtimes installed. It has been tested with the versions listed below

- Python (3.11)  
  [https://www.python.org/downloads](https://www.python.org/downloads)

- R and Rtools (4.2.3)  
  [https://cran.r-project.org/bin/windows/base](https://cran.r-project.org/bin/windows/base)
  [https://cran.r-project.org/bin/windows/Rtools/](https://cran.r-project.org/bin/windows/Rtools/)

Relevant documentation should also be followed to ensure runtimes can be executed from PATH environment variable.

## Configuration

**Environment**
Create an environment file from the sample. These will be populated using [Pydantic](https://docs.pydantic.dev/usage/settings/)

```
cp .env.sample .env
```

**Python**
The scripts below will create a python [virtual environment](https://docs.python.org/3/library/venv.html), activate, install required python and R dependencies and start local server

=== "Windows (powershell)"

    ``` ps1 linenums="1"
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    pip install -r requirements_picsa.txt
    uvicorn app.main:app --reload
    ```

=== "Linux (bash)"

    ```sh linenums="1"
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip install -r requirements_picsa.txt
    uvicorn app.main:app --reload
    ```

**R**
Once installed you will need to call R from an elevated shell to install dependencies

Windows (run as administrator)

```
Rscript install_packages.R
Rscript install_packages_picsa.R
```

Linux

```
sudo Rscript install_packages.R
sudo Rscript install_packages_picsa.R
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

## Troubleshooting

**Pip won't install dependencies**
Depending on local versions of R and python (as well as operating system) there may be issues when installing certain packages. Recommend attempting install using the `requirements_dev.txt` file which pins exact versions of packages shown to be compatible with each other, i.e.

```sh
pip install -r requirements_dev.txt
```

Any other issues should be raised on GitHub

## License

This project is licensed under the terms of the MIT license.
