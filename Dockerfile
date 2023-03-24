# FastAPI base image (builds on python official debian image, currently bullseye)
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Allow python to find locally installed modules
ENV PYTHONPATH "${PYTHONPATH}:/app"
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

# Install R core dependencies (adapted from https://hub.docker.com/r/thomaschln/r-devtools/dockerfile)
# https://github.com/guigolab/ggsashimi/issues/45
COPY ./install_packages.R /app/
RUN apt-get install -y libcurl4-openssl-dev libssl-dev libssh2-1-dev libxml2-dev zlib1g-dev libharfbuzz-dev libfribidi-dev && \
  Rscript ./install_packages.R

# Install Python core dependencies
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir --default-timeout=100 --upgrade -r requirements.txt

# Install linked picsa python and R repos
# Perform last to allow caching of steps above
COPY ./requirements_picsa.txt /app/
RUN pip install --no-cache-dir --default-timeout=100 --upgrade -r requirements_picsa.txt

COPY ./install_packages_picsa.R /app/
RUN Rscript ./install_packages_picsa.R

COPY ./app /app
