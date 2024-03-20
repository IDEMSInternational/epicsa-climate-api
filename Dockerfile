# FastAPI base image (builds on python official debian image, currently bullseye)
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Set a top-level folder that will be used to host all files
# Matches https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/master/docker-images/python3.11.dockerfile
WORKDIR /app

# Allow python to find locally installed modules
ENV PYTHONPATH "/app"
ENV PORT=8000

# Install core dependencies for adding R and python dependencies
RUN apt update && \
  apt-get install --yes --no-install-recommends \
    build-essential \
    gcc \
    libcurl4-openssl-dev \
    libfribidi-dev \
    libharfbuzz-dev \
    libnetcdf-dev \
    libpq-dev \
    libssh2-1-dev \
    libssl-dev \
    libxml2-dev \
    r-base \
    r-base-dev \
    r-cran-devtools \
    software-properties-common \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

# Install R dependencies
COPY ./install_packages_picsa.R .
RUN Rscript ./install_packages_picsa.R

# Install Python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 --upgrade -r requirements.txt

# Copy runtime application (will sit in nested /app/app as expected by uvicorn gunicorn)
COPY ./app ./app

COPY ./entrypoint.sh .
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/start.sh"]
