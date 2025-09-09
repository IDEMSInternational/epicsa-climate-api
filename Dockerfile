# -------- BUILDER STAGE --------
FROM python:3.13-bookworm AS builder

WORKDIR /work

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add R repository key and repository
RUN gpg --keyserver keyserver.ubuntu.com \
    --recv-key '95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7' \
    && gpg --armor --export '95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7' | \
    gpg --dearmor -o /etc/apt/trusted.gpg.d/cran_debian_key.gpg \
    && echo "deb https://cloud.r-project.org/bin/linux/debian bookworm-cran40/" > \
    /etc/apt/sources.list.d/cran40.list

# Install R
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Verify installation (optional)
RUN R --version

# Install R packages
COPY install_packages_picsa.R .
RUN Rscript install_packages_picsa.R

# Set up Python virtual environment
RUN python -m venv /opt/idems/venv
ENV PATH=/opt/idems/venv/bin:${PATH}
ENV PIP_NO_CACHE_DIR=1
COPY requirements.txt .
RUN pip install --upgrade -r requirements.txt


# -------- PROD STAGE --------
FROM python:3.13-slim-bookworm AS prod
WORKDIR /app

ENV PATH=/opt/idems/venv/bin:${PATH}
ENV PIP_NO_CACHE_DIR=1
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000

# Copy GPG key and R repository config from builder
COPY --from=builder /etc/apt/trusted.gpg.d/cran_debian_key.gpg /etc/apt/trusted.gpg.d/
COPY --from=builder /etc/apt/sources.list.d/cran40.list /etc/apt/sources.list.d/

# Install only runtime R dependencies (no dev tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    mariadb-client-core \
    r-base \
    r-cran-magrittr \
    r-cran-memoise \
    r-cran-pkgconfig \
    r-cran-r6 && \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy installed R packages & Python venv from builder
COPY --from=builder /usr/local/lib/R/site-library /usr/local/lib/R/site-library
COPY --from=builder /opt/idems/venv /opt/idems/venv

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app
USER appuser

# Copy app source
COPY --chown=appuser:appuser app app
COPY --chown=appuser:appuser entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app"]