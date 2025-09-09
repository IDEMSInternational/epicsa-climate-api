FROM python:3.11-bookworm AS builder

WORKDIR /work

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
    software-properties-common \
    zlib1g-dev

COPY install_packages_picsa.R .
RUN Rscript install_packages_picsa.R

RUN python -m venv /opt/idems/venv
ENV PATH=/opt/idems/venv/bin:${PATH}
ENV PIP_NO_CACHE_DIR=1
COPY requirements.txt .
RUN pip install --upgrade -r requirements.txt

FROM python:3.11-slim-bookworm AS prod
WORKDIR /app
ENV PATH=/opt/idems/venv/bin:${PATH}
ENV PIP_NO_CACHE_DIR=1
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000

RUN apt update && \
  apt-get install --yes --no-install-recommends \
    mariadb-client-core \
    r-base \
    r-cran-magrittr \
    r-cran-memoise \
    r-cran-pkgconfig \
    r-cran-r6 && \
  rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/lib/R/site-library /usr/local/lib/R/site-library
COPY --from=builder /opt/idems/venv /opt/idems/venv
COPY app app
COPY entrypoint.sh .

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app"]
