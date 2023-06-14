# E-PICSA Climate Api

API for accessing E-PICSA climate services

Build with [FastAPI](https://fastapi.tiangolo.com/)

## Pre-Requisites

The api requires Python and R runtimes installed. It has been tested with the versions listed below

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

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install --upgrade -r requirements.txt
    pip install --upgrade --no-cache-dir -r requirements_picsa.txt
    uvicorn app.main:app --reload

=== "Linux (bash)"

    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade -r requirements.txt
    pip install --upgrade --no-cache-dir -r requirements_picsa.txt
    uvicorn app.main:app --reload

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

**Authorization File**

In order to run the package, you will need to add the following service account file to the main repository folder (i.e. the folder where this `README.md` file is stored):

```
service-account.json
```

## Running locally

Once installed, subsequent server starts can skip installation steps

=== "Windows (powershell)"

    .\.venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload

=== "Linux (bash)"

    source .venv/bin/activate
    uvicorn app.main:app --reload

The server will start at [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Running Tests

```py
pytest
```

## Deployment

This repo contains example workflow to build as a docker image and deploy to google cloud run. See action yaml for details

## Troubleshooting

**Pip won't install dependencies**
Depending on local versions of R and python (as well as operating system) there may be issues when installing certain packages. Recommend attempting install using the `requirements_dev.txt` file which pins exact versions of packages shown to be compatible with each other, i.e.

```sh
pip install --upgrade -r requirements_dev.txt
```

**Called endpoint method does not exist**
The library calls methods from various other git repos where code is hosted both in python and R. These are installed during initial setup, but will need reinstallation whenever new versions of the external repos exist.

Simply repeat the steps above to install dependencies from `requirements_picsa.txt` `install_packages_picsa.R`

Any other issues should be raised on GitHub

## License

This project is licensed under the terms of the MIT license.
