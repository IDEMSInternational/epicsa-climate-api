# FastAPI base image (builds on python official debian image, currently bullseye)
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PORT=8000

# Install core dependencies for adding R and python dependencies
RUN apt-get update && \
  apt-get install -y software-properties-common build-essential libpq-dev libnetcdf-dev gcc \
  && rm -rf /var/lib/apt/lists/*

# Install R v4
# https://cran.r-project.org/bin/linux/debian/
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key '95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7' && \
  add-apt-repository 'deb http://cloud.r-project.org/bin/linux/debian bullseye-cran40/' && \
  apt update && \
  apt-get install -y --no-install-recommends r-base r-base-dev

# Install R core deps devtools & rlang (adapted from https://hub.docker.com/r/thomaschln/r-devtools/dockerfile)
# https://github.com/guigolab/ggsashimi/issues/45
RUN apt-get install -y libcurl4-openssl-dev libssl-dev libssh2-1-dev libxml2-dev zlib1g-dev libharfbuzz-dev libfribidi-dev && \
  R -e "install.packages(c('devtools','rlang'))"

# Setup virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip

# Install python dependencies
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir --default-timeout=100 --upgrade -r requirements.txt

## Install additional R dependencies
COPY ./install_packages.R /app/
RUN Rscript ./install_packages.R

COPY ./app /app
